import logging

from django.utils import timezone

from journal.models import TAG_COLORS, JournalEntry, Tag
from journal.services.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


def auto_tag_entry(entry_id: int) -> None:
    """Auto-tag a single journal entry using Ollama. Safe to call from a background thread."""
    try:
        entry = JournalEntry.objects.get(id=entry_id)
    except JournalEntry.DoesNotExist:
        logger.warning("auto_tag_entry: entry %d not found", entry_id)
        return

    client = OllamaClient()
    if not client.is_available():
        logger.warning(
            "auto_tag_entry: Ollama not available at %s, skipping entry %d",
            client.base_url,
            entry_id,
        )
        return

    tag_names = client.generate_tags(entry.content)
    entry.tags.clear()

    for i, tag_name in enumerate(tag_names):
        tag, _ = Tag.objects.get_or_create(
            name=tag_name,
            user=entry.user,
            defaults={"color": TAG_COLORS[i % len(TAG_COLORS)]},
        )
        entry.tags.add(tag)

    entry.tagged_at = timezone.now()
    entry.save(update_fields=["tagged_at"])
    logger.info("auto_tag_entry: tagged entry %d with %s", entry_id, tag_names)
