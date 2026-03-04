import json
import random
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import CustomRegisterForm, JournalEntryForm
from .models import TAG_COLORS, JournalEntry, Tag, UserProfile


@login_required
def journal_view(request):
    """Main journal view with entry form and calendar."""
    form = JournalEntryForm()
    today = timezone.now().date()
    entries = JournalEntry.objects.filter(
        user=request.user, timestamp__date=today
    ).prefetch_related("tags")

    # Get random entry from the past
    random_entry = None
    past_entries = JournalEntry.objects.filter(
        user=request.user, timestamp__date__lt=today
    )
    if past_entries.exists():
        random_entry = random.choice(list(past_entries))

    # Get dates with entries for the calendar indicator
    dates_with_entries = (
        JournalEntry.objects.filter(user=request.user)
        .values_list("timestamp__date", flat=True)
        .distinct()
        .order_by("timestamp__date")
    )

    return render(
        request,
        "journal/journal.html",
        {
            "form": form,
            "entries": entries,
            "selected_date": today,
            "today": today,
            "random_entry": random_entry,
            "dates_with_entries": list(dates_with_entries),
        },
    )


@login_required
@require_http_methods(["POST"])
def create_entry_view(request):
    """Handle creation of new journal entries (HTMX endpoint)."""
    form = JournalEntryForm(request.POST)

    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()

        today = timezone.now().date()
        entries = JournalEntry.objects.filter(
            user=request.user, timestamp__date=today
        ).prefetch_related("tags")
        return render(
            request,
            "journal/partials/entries.html",
            {
                "entries": entries,
                "selected_date": today,
                "entry_saved": True,
            },
        )

    return HttpResponse("Invalid form", status=400)


@login_required
def get_entries_by_date(request):
    """Get journal entries for a specific date (HTMX endpoint)."""
    date_str = request.GET.get("date")

    if not date_str:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    try:
        selected_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    entries = JournalEntry.objects.filter(
        user=request.user, timestamp__date=selected_date
    ).prefetch_related("tags")

    return render(
        request,
        "journal/partials/entries.html",
        {
            "entries": entries,
            "selected_date": selected_date,
            "target_id": "past-entries-container",
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_entry_view(request, entry_id):
    """Delete a specific journal entry."""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)

    entry_date = entry.timestamp.date()
    target_id = request.GET.get("target", "entries-list")

    entry.delete()

    entries = JournalEntry.objects.filter(
        user=request.user, timestamp__date=entry_date
    ).prefetch_related("tags")

    context = {
        "entries": entries,
        "selected_date": entry_date,
    }

    if target_id == "past-entries-container":
        context["target_id"] = target_id

    return render(request, "journal/partials/entries.html", context)


def register_view(request):
    """Handle user registration."""
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("journal")
    else:
        form = CustomRegisterForm()
    return render(request, "journal/register.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def update_theme(request):
    """Update user theme preference."""
    theme = request.POST.get("theme")
    if theme in dict(UserProfile.THEME_CHOICES):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.theme = theme
        profile.save()
    return HttpResponse(status=204)


@login_required
def entry_tags_status_view(request, entry_id):
    """Return the tags partial for a single entry. Used by HTMX polling."""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    return render(request, "journal/partials/entry_tags.html", {"entry": entry})


@login_required
@require_http_methods(["POST"])
def add_tag_view(request, entry_id):
    """Add a tag to a journal entry."""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    tag_name = request.POST.get("tag_name", "").strip().lower()[:50]

    if not tag_name:
        return HttpResponse("Tag name is required", status=400)

    existing_count = Tag.objects.filter(user=request.user).count()
    tag, _ = Tag.objects.get_or_create(
        name=tag_name,
        user=request.user,
        defaults={"color": TAG_COLORS[existing_count % len(TAG_COLORS)]},
    )
    entry.tags.add(tag)

    entries = JournalEntry.objects.filter(
        user=request.user, timestamp__date=entry.timestamp.date()
    ).prefetch_related("tags")
    return render(
        request,
        "journal/partials/entries.html",
        {"entries": entries, "selected_date": entry.timestamp.date()},
    )


@login_required
@require_http_methods(["DELETE"])
def remove_tag_view(request, entry_id, tag_id):
    """Remove a tag from a journal entry."""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    tag = get_object_or_404(Tag, id=tag_id, user=request.user)
    entry.tags.remove(tag)

    # Clean up orphaned tags
    if not tag.entries.exists():
        tag.delete()

    return HttpResponse("")


@login_required
def export_data_view(request):
    """Export all journal entries for the logged-in user as JSON."""
    entries = (
        JournalEntry.objects.filter(user=request.user)
        .prefetch_related("tags")
        .order_by("timestamp")
    )

    data = {
        "exported_at": timezone.now().isoformat(),
        "username": request.user.username,
        "version": 1,
        "entries": [
            {
                "content": entry.content,
                "timestamp": entry.timestamp.isoformat(),
                "tags": [tag.name for tag in entry.tags.all()],
            }
            for entry in entries
        ],
    }

    filename = f"reflections_export_{timezone.now().strftime('%Y%m%d')}.json"
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_http_methods(["POST"])
def import_data_view(request):
    """Import journal entries from a JSON file."""
    file = request.FILES.get("file")
    if not file:
        messages.error(request, "No file provided.")
        return redirect("journal")

    try:
        data = json.loads(file.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        messages.error(request, "Invalid JSON file.")
        return redirect("journal")

    if not isinstance(data, dict) or "entries" not in data:
        messages.error(request, "Invalid export format.")
        return redirect("journal")

    imported = 0
    skipped = 0

    for item in data.get("entries", []):
        try:
            timestamp = datetime.fromisoformat(item["timestamp"])
            content = item["content"]
        except (KeyError, ValueError):
            skipped += 1
            continue

        entry, created = JournalEntry.objects.get_or_create(
            user=request.user,
            timestamp=timestamp,
            content=content,
        )

        if created:
            for tag_name in item.get("tags", []):
                tag_name = tag_name.strip().lower()[:50]
                if tag_name:
                    existing_count = Tag.objects.filter(user=request.user).count()
                    tag, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        user=request.user,
                        defaults={
                            "color": TAG_COLORS[existing_count % len(TAG_COLORS)]
                        },
                    )
                    entry.tags.add(tag)
            imported += 1
        else:
            skipped += 1

    messages.success(
        request, f"Import complete: {imported} entries imported, {skipped} skipped."
    )
    return redirect("journal")
