import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from journal.models import JournalEntry


class TestAuthenticationViews(TestCase):
    """Test authentication views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal Journal")

    def test_login_success(self):
        """Test successful login redirects to journal."""
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("journal"))

    def test_login_failure(self):
        """Test failed login shows error."""
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")

    def test_register_page_loads(self):
        """Test that register page loads successfully."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    def test_register_success(self):
        """Test successful registration creates user and redirects."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "complexpass123!",
                "password2": "complexpass123!",
            },
        )
        self.assertRedirects(response, reverse("journal"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        """Test registering with existing username shows error."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",  # Already exists
                "password1": "complexpass123!",
                "password2": "complexpass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        # Django's built-in validation catches this
        self.assertContains(response, "already exists")

    def test_logout_requires_post(self):
        """Test that logout requires POST request."""
        self.client.login(username="testuser", password="testpass123")
        # GET request should be rejected
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_logout_post_success(self):
        """Test successful logout via POST."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))


class TestJournalViews(TestCase):
    """Test journal views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_journal_requires_login(self):
        """Test that journal page requires authentication."""
        self.client.logout()
        response = self.client.get(reverse("journal"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('journal')}")

    def test_journal_page_loads(self):
        """Test that journal page loads for authenticated user."""
        response = self.client.get(reverse("journal"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Entry")

    def test_create_entry(self):
        """Test creating a new journal entry."""
        response = self.client.post(
            reverse("create_entry"),
            {"content": "Test journal entry content"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            JournalEntry.objects.filter(
                user=self.user, content="Test journal entry content"
            ).exists()
        )

    def test_create_entry_empty_content(self):
        """Test that empty content is rejected."""
        response = self.client.post(
            reverse("create_entry"),
            {"content": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(JournalEntry.objects.count(), 0)

    def test_get_entries_by_date(self):
        """Test fetching entries for a specific date."""
        # Create an entry for today
        today = timezone.now().date()
        JournalEntry.objects.create(user=self.user, content="Today entry")

        response = self.client.get(
            reverse("get_entries"),
            {"date": today.strftime("%Y-%m-%d")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Today entry")

    def test_get_entries_invalid_date(self):
        """Test that invalid date format returns error."""
        response = self.client.get(
            reverse("get_entries"),
            {"date": "invalid-date"},
        )
        self.assertEqual(response.status_code, 400)

    def test_get_entries_missing_date(self):
        """Test that missing date parameter returns error."""
        response = self.client.get(reverse("get_entries"))
        self.assertEqual(response.status_code, 400)

    def test_entries_user_isolation(self):
        """Test that users can only see their own entries."""
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )
        JournalEntry.objects.create(user=other_user, content="Other user's entry")
        JournalEntry.objects.create(user=self.user, content="My entry")

        today = timezone.now().date()
        response = self.client.get(
            reverse("get_entries"),
            {"date": today.strftime("%Y-%m-%d")},
        )
        self.assertContains(response, "My entry")
        self.assertNotContains(response, "Other user's entry")


class TestJournalModel(TestCase):
    """Test JournalEntry model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_entry_creation(self):
        """Test creating a journal entry."""
        entry = JournalEntry.objects.create(user=self.user, content="Test content")
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.content, "Test content")
        self.assertIsNotNone(entry.timestamp)

    def test_entry_ordering(self):
        """Test that entries are ordered by timestamp descending."""
        entry1 = JournalEntry.objects.create(user=self.user, content="First")
        entry2 = JournalEntry.objects.create(user=self.user, content="Second")

        entries = list(JournalEntry.objects.all())
        self.assertEqual(entries[0], entry2)  # Most recent first
        self.assertEqual(entries[1], entry1)

    def test_entry_str(self):
        """Test string representation of entry."""
        entry = JournalEntry.objects.create(user=self.user, content="Test content")
        self.assertIn("testuser", str(entry))
