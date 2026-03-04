import threading

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

TAG_COLORS = [
    "#8b5e3c",  # warm brown
    "#6b7c5e",  # sage green
    "#7c6c8a",  # muted purple
    "#8a6b5e",  # dusty rose
    "#5e7c8a",  # slate blue
    "#8a8b5e",  # olive
    "#5e6b8a",  # steel blue
    "#8a5e6b",  # mauve
]


class Tag(models.Model):
    """Tag for categorizing journal entries. Scoped per-user."""

    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    color = models.CharField(max_length=7, default="#6b7280")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "user")
        ordering = ["name"]

    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    """Model for journal entries."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="journal_entries"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="entries")
    tagged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this entry was last auto-tagged by the LLM",
    )

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]


class UserProfile(models.Model):
    """Model for user preferences."""

    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("system", "System"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="system")

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=JournalEntry)
def schedule_auto_tagging(sender, instance, **kwargs):
    """Spawn a background thread to auto-tag the entry when it has no tags yet."""
    if getattr(settings, "AUTO_TAG_ON_SAVE", True) and instance.tagged_at is None:
        from journal.services.tagging import auto_tag_entry

        thread = threading.Thread(
            target=auto_tag_entry, args=(instance.id,), daemon=True
        )
        thread.start()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Check if profile exists (for existing users who might not have one yet)
    if hasattr(instance, "profile"):
        instance.profile.save()
