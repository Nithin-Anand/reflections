import json
import urllib.error
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from journal.models import JournalEntry, Tag
from journal.services.ollama_client import OllamaClient
from journal.services.tagging import auto_tag_entry


class TestTagModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_tag_creation(self):
        tag = Tag.objects.create(name="work", user=self.user)
        self.assertEqual(tag.name, "work")
        self.assertEqual(tag.user, self.user)
        self.assertIsNotNone(tag.color)

    def test_tag_unique_per_user(self):
        Tag.objects.create(name="work", user=self.user)
        with self.assertRaises(Exception):
            Tag.objects.create(name="work", user=self.user)

    def test_same_tag_name_different_users(self):
        other_user = User.objects.create_user(username="other", password="testpass123")
        tag1 = Tag.objects.create(name="work", user=self.user)
        tag2 = Tag.objects.create(name="work", user=other_user)
        self.assertNotEqual(tag1.id, tag2.id)

    def test_entry_tag_m2m(self):
        entry = JournalEntry.objects.create(user=self.user, content="Test")
        tag = Tag.objects.create(name="test", user=self.user)
        entry.tags.add(tag)
        self.assertIn(tag, entry.tags.all())

    def test_tagged_at_defaults_null(self):
        entry = JournalEntry.objects.create(user=self.user, content="Test")
        self.assertIsNone(entry.tagged_at)


class TestTagViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        self.entry = JournalEntry.objects.create(user=self.user, content="Test entry")

    def test_add_tag(self):
        response = self.client.post(
            reverse("add_tag", args=[self.entry.id]),
            {"tag_name": "work"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.entry.tags.filter(name="work").exists())

    def test_add_tag_normalises_case(self):
        response = self.client.post(
            reverse("add_tag", args=[self.entry.id]),
            {"tag_name": "Work"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.entry.tags.filter(name="work").exists())

    def test_add_empty_tag_rejected(self):
        response = self.client.post(
            reverse("add_tag", args=[self.entry.id]),
            {"tag_name": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_add_tag_reuses_existing(self):
        Tag.objects.create(name="work", user=self.user, color="#ff0000")
        response = self.client.post(
            reverse("add_tag", args=[self.entry.id]),
            {"tag_name": "work"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tag.objects.filter(name="work", user=self.user).count(), 1)

    def test_remove_tag(self):
        tag = Tag.objects.create(name="work", user=self.user)
        self.entry.tags.add(tag)

        response = self.client.delete(
            reverse("remove_tag", args=[self.entry.id, tag.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.entry.tags.filter(name="work").exists())

    def test_remove_tag_deletes_orphan(self):
        tag = Tag.objects.create(name="orphan", user=self.user)
        self.entry.tags.add(tag)

        self.client.delete(reverse("remove_tag", args=[self.entry.id, tag.id]))
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_remove_tag_keeps_shared_tag(self):
        """Tag used by another entry should not be deleted."""
        tag = Tag.objects.create(name="shared", user=self.user)
        other_entry = JournalEntry.objects.create(user=self.user, content="Other")
        self.entry.tags.add(tag)
        other_entry.tags.add(tag)

        self.client.delete(reverse("remove_tag", args=[self.entry.id, tag.id]))
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_cannot_tag_other_users_entry(self):
        other_user = User.objects.create_user(username="other", password="pass123")
        other_entry = JournalEntry.objects.create(user=other_user, content="Private")

        response = self.client.post(
            reverse("add_tag", args=[other_entry.id]),
            {"tag_name": "hacked"},
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_remove_tag_from_other_users_entry(self):
        other_user = User.objects.create_user(username="other", password="pass123")
        other_entry = JournalEntry.objects.create(user=other_user, content="Private")
        tag = Tag.objects.create(name="work", user=other_user)
        other_entry.tags.add(tag)

        response = self.client.delete(
            reverse("remove_tag", args=[other_entry.id, tag.id]),
        )
        self.assertEqual(response.status_code, 404)

    def test_tags_visible_in_entries_list(self):
        tag = Tag.objects.create(name="gratitude", user=self.user, color="#6b7c5e")
        self.entry.tags.add(tag)
        self.entry.tagged_at = timezone.now()
        self.entry.save(update_fields=["tagged_at"])

        date_str = self.entry.timestamp.date().strftime("%Y-%m-%d")
        response = self.client.get(reverse("get_entries"), {"date": date_str})
        self.assertContains(response, "gratitude")


class TestAutoTagEntry(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tagger", password="pass")
        self.entry = JournalEntry.objects.create(
            user=self.user, content="Stressed about work deadlines"
        )

    @patch("journal.services.tagging.OllamaClient")
    def test_tags_applied_and_tagged_at_set(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.is_available.return_value = True
        mock_instance.generate_tags.return_value = ["work", "stress"]

        auto_tag_entry(self.entry.id)

        self.entry.refresh_from_db()
        self.assertIsNotNone(self.entry.tagged_at)
        self.assertTrue(self.entry.tags.filter(name="work").exists())
        self.assertTrue(self.entry.tags.filter(name="stress").exists())

    @patch("journal.services.tagging.OllamaClient")
    def test_ollama_unavailable_skips_tagging(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.is_available.return_value = False

        auto_tag_entry(self.entry.id)

        self.entry.refresh_from_db()
        self.assertIsNone(self.entry.tagged_at)
        self.assertEqual(self.entry.tags.count(), 0)

    @patch("journal.services.tagging.OllamaClient")
    def test_no_tags_returned_still_sets_tagged_at(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.is_available.return_value = True
        mock_instance.generate_tags.return_value = []

        auto_tag_entry(self.entry.id)

        self.entry.refresh_from_db()
        self.assertIsNotNone(self.entry.tagged_at)
        self.assertEqual(self.entry.tags.count(), 0)

    def test_nonexistent_entry_id_does_not_raise(self):
        auto_tag_entry(entry_id=99999)  # Should log and return gracefully

    @patch("journal.services.tagging.OllamaClient")
    def test_existing_tags_cleared_before_retagging(self, MockClient):
        old_tag = Tag.objects.create(name="old", user=self.user)
        self.entry.tags.add(old_tag)
        mock_instance = MockClient.return_value
        mock_instance.is_available.return_value = True
        mock_instance.generate_tags.return_value = ["new"]

        auto_tag_entry(self.entry.id)

        self.entry.refresh_from_db()
        self.assertFalse(self.entry.tags.filter(name="old").exists())
        self.assertTrue(self.entry.tags.filter(name="new").exists())


class TestAutoTagSignal(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="signaluser", password="pass")

    @patch("journal.models.threading.Thread")
    def test_signal_spawns_thread_on_entry_create(self, MockThread):
        mock_thread = MagicMock()
        MockThread.return_value = mock_thread

        with self.settings(AUTO_TAG_ON_SAVE=True):
            JournalEntry.objects.create(user=self.user, content="New entry")

        MockThread.assert_called_once()
        mock_thread.start.assert_called_once()

    @patch("journal.models.threading.Thread")
    def test_signal_does_not_spawn_thread_when_already_tagged(self, MockThread):
        entry = JournalEntry.objects.create(user=self.user, content="Already tagged")
        MockThread.reset_mock()

        entry.tagged_at = timezone.now()
        entry.save(update_fields=["tagged_at"])

        MockThread.assert_not_called()


class TestEntryTagsStatusView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="viewuser", password="pass")
        self.client.login(username="viewuser", password="pass")
        self.entry = JournalEntry.objects.create(user=self.user, content="Test")

    def test_status_view_returns_spinner_when_untagged(self):
        response = self.client.get(reverse("entry_tags_status", args=[self.entry.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "analyzing")
        self.assertContains(response, "every 3s")

    def test_status_view_returns_tags_when_tagged(self):
        self.entry.tagged_at = timezone.now()
        self.entry.save(update_fields=["tagged_at"])
        tag = Tag.objects.create(name="health", user=self.user, color="#5e7c8a")
        self.entry.tags.add(tag)

        response = self.client.get(reverse("entry_tags_status", args=[self.entry.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "health")
        self.assertNotContains(response, "analyzing")
        self.assertNotContains(response, "every 3s")

    def test_status_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("entry_tags_status", args=[self.entry.id]))
        self.assertEqual(response.status_code, 302)

    def test_status_view_rejects_other_users_entry(self):
        other = User.objects.create_user(username="other2", password="pass")
        other_entry = JournalEntry.objects.create(user=other, content="Private")
        response = self.client.get(reverse("entry_tags_status", args=[other_entry.id]))
        self.assertEqual(response.status_code, 404)


class TestOllamaClient(TestCase):
    @patch("journal.services.ollama_client.urllib.request.urlopen")
    def test_is_available_returns_true(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = OllamaClient(base_url="http://localhost:11434")
        self.assertTrue(client.is_available())

    @patch("journal.services.ollama_client.urllib.request.urlopen")
    def test_is_available_returns_false_on_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")

        client = OllamaClient(base_url="http://localhost:11434")
        self.assertFalse(client.is_available())

    @patch("journal.services.ollama_client.urllib.request.urlopen")
    def test_generate_tags_returns_list(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"response": '["work", "frustration", "goals"]'}
        ).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = OllamaClient(base_url="http://localhost:11434")
        tags = client.generate_tags("I had a tough day at work...")
        self.assertEqual(tags, ["work", "frustration", "goals"])

    @patch("journal.services.ollama_client.urllib.request.urlopen")
    def test_generate_tags_capped_at_five(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"response": '["a", "b", "c", "d", "e", "f", "g"]'}
        ).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = OllamaClient(base_url="http://localhost:11434")
        tags = client.generate_tags("entry text")
        self.assertEqual(len(tags), 5)

    @patch("journal.services.ollama_client.urllib.request.urlopen")
    def test_generate_tags_handles_network_failure(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("fail")

        client = OllamaClient(base_url="http://localhost:11434")
        tags = client.generate_tags("anything")
        self.assertEqual(tags, [])

    @patch("journal.services.ollama_client.urllib.request.urlopen")
    def test_generate_tags_handles_invalid_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"response": "here are some tags: work, family"}
        ).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = OllamaClient(base_url="http://localhost:11434")
        tags = client.generate_tags("entry text")
        self.assertEqual(tags, [])
