from django.contrib import admin

from journal.models import JournalEntry


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin interface for JournalEntry model."""

    list_display = ["user", "timestamp", "content_preview"]
    list_filter = ["user", "timestamp"]
    search_fields = ["content", "user__username"]
    date_hierarchy = "timestamp"
    readonly_fields = ["timestamp", "updated_at"]

    def content_preview(self, obj):
        """Show first 50 characters of content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"
