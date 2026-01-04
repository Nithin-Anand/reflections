from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class JournalEntry(models.Model):
    """Model for journal entries."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="journal_entries"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Check if profile exists (for existing users who might not have one yet)
    if hasattr(instance, "profile"):
        instance.profile.save()
