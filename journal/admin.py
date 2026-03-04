from django.contrib import admin

from journal.models import JournalEntry, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color", "created_at"]
    list_filter = ["user"]
    search_fields = ["name", "user__username"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin interface for JournalEntry model."""

    list_display = ["user", "timestamp", "content_preview", "tag_list"]
    list_filter = ["user", "timestamp"]
    search_fields = ["content", "user__username"]
    date_hierarchy = "timestamp"
    readonly_fields = ["timestamp", "updated_at", "tagged_at"]
    filter_horizontal = ("tags",)

    def content_preview(self, obj):
        """Show first 50 characters of content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def tag_list(self, obj):
        return ", ".join(t.name for t in obj.tags.all())

    tag_list.short_description = "Tags"
