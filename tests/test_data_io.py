import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from journal.models import JournalEntry, Tag


class TestExportImport(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        self.entry = JournalEntry.objects.create(
            user=self.user,
            content="Test entry content",
            timestamp=timezone.now(),
        )
        self.tag = Tag.objects.create(
            user=self.user, name="reflection", color="#aabbcc"
        )
        self.entry.tags.add(self.tag)

    def test_export_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("export_data"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('export_data')}"
        )

    def test_export_returns_json_file(self):
        response = self.client.get(reverse("export_data"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".json", response["Content-Disposition"])

    def test_export_contains_all_entries(self):
        JournalEntry.objects.create(
            user=self.user, content="Second entry", timestamp=timezone.now()
        )
        response = self.client.get(reverse("export_data"))
        data = json.loads(response.content)
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(len(data["entries"]), 2)

    def test_export_includes_tags(self):
        response = self.client.get(reverse("export_data"))
        data = json.loads(response.content)
        entry_data = data["entries"][0]
        self.assertIn("tags", entry_data)
        self.assertIn("reflection", entry_data["tags"])

    def test_export_isolates_by_user(self):
        JournalEntry.objects.create(
            user=self.other_user, content="Other user entry", timestamp=timezone.now()
        )
        response = self.client.get(reverse("export_data"))
        data = json.loads(response.content)
        self.assertEqual(len(data["entries"]), 1)
        self.assertEqual(data["entries"][0]["content"], "Test entry content")

    def _make_import_file(self, entries, version=1, username="testuser"):
        payload = {
            "version": version,
            "username": username,
            "exported_at": timezone.now().isoformat(),
            "entries": entries,
        }
        return (json.dumps(payload).encode(), "export.json", "application/json")

    def test_import_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("import_data"), {})
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('import_data')}"
        )

    def test_import_creates_entries(self):
        JournalEntry.objects.all().delete()
        content, name, ctype = self._make_import_file(
            [
                {
                    "content": "Imported entry",
                    "timestamp": "2026-01-01T10:00:00+00:00",
                    "tags": ["joy"],
                },
            ]
        )
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile(name, content, content_type=ctype)
        response = self.client.post(reverse("import_data"), {"file": f})
        self.assertRedirects(response, reverse("journal"))
        self.assertEqual(JournalEntry.objects.filter(user=self.user).count(), 1)
        self.assertEqual(
            JournalEntry.objects.filter(user=self.user).first().content,
            "Imported entry",
        )
        self.assertTrue(Tag.objects.filter(user=self.user, name="joy").exists())

    def test_import_skips_duplicates(self):
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile

        timestamp = self.entry.timestamp.isoformat()
        content, name, ctype = self._make_import_file(
            [
                {"content": self.entry.content, "timestamp": timestamp, "tags": []},
            ]
        )
        f = SimpleUploadedFile(name, content, content_type=ctype)
        self.client.post(reverse("import_data"), {"file": f})
        # Should still be 1 entry, not 2
        self.assertEqual(JournalEntry.objects.filter(user=self.user).count(), 1)

    def test_import_rejects_invalid_json(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile(
            "bad.json", b"not valid json", content_type="application/json"
        )
        response = self.client.post(reverse("import_data"), {"file": f})
        self.assertRedirects(response, reverse("journal"))
        # Verify error message in session
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Invalid" in str(m) for m in messages))

    def test_import_rejects_missing_entries_key(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile(
            "bad.json", b'{"version": 1}', content_type="application/json"
        )
        response = self.client.post(reverse("import_data"), {"file": f})
        self.assertRedirects(response, reverse("journal"))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Invalid" in str(m) for m in messages))

    def test_import_user_isolation(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        content, name, ctype = self._make_import_file(
            [
                {
                    "content": "Isolated entry",
                    "timestamp": "2026-02-01T10:00:00+00:00",
                    "tags": [],
                },
            ]
        )
        f = SimpleUploadedFile(name, content, content_type=ctype)
        self.client.post(reverse("import_data"), {"file": f})
        self.assertFalse(
            JournalEntry.objects.filter(
                user=self.other_user, content="Isolated entry"
            ).exists()
        )
        self.assertTrue(
            JournalEntry.objects.filter(
                user=self.user, content="Isolated entry"
            ).exists()
        )

    def test_import_no_file(self):
        response = self.client.post(reverse("import_data"), {})
        self.assertRedirects(response, reverse("journal"))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("No file" in str(m) for m in messages))
