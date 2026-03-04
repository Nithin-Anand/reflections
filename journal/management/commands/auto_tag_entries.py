import logging

from django.core.management.base import BaseCommand

from journal.models import JournalEntry
from journal.services.ollama_client import OllamaClient
from journal.services.tagging import auto_tag_entry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Auto-tag journal entries using Ollama LLM"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum number of entries to process per run (default: 50)",
        )
        parser.add_argument(
            "--retag",
            action="store_true",
            help="Re-tag all entries, including those already tagged",
        )

    def handle(self, *args, **options):
        client = OllamaClient()

        if not client.is_available():
            self.stderr.write(
                self.style.WARNING(
                    f"Ollama is not available at {client.base_url}. Skipping auto-tagging."
                )
            )
            return

        self.stdout.write(
            f"Connected to Ollama at {client.base_url} (model: {client.model})"
        )

        if options["retag"]:
            queryset = JournalEntry.objects.all()
        else:
            queryset = JournalEntry.objects.filter(tagged_at__isnull=True)

        entries = queryset.order_by("-timestamp")[: options["limit"]]
        total = entries.count()

        if total == 0:
            self.stdout.write("No entries need tagging.")
            return

        self.stdout.write(f"Found {total} entries to tag.")

        for i, entry in enumerate(entries, 1):
            self.stdout.write(f"  [{i}/{total}] Tagging entry {entry.id}...")
            auto_tag_entry(entry.id)
            entry.refresh_from_db(fields=["tagged_at", "tags"])
            tag_names = [t.name for t in entry.tags.all()]
            if tag_names:
                self.stdout.write(
                    self.style.SUCCESS(f"    Tagged: {', '.join(tag_names)}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"    No tags returned for entry {entry.id}")
                )

        self.stdout.write(self.style.SUCCESS("Auto-tagging complete."))
