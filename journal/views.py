from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import random

from .models import JournalEntry, UserProfile
from .forms import JournalEntryForm, CustomRegisterForm


@login_required
def journal_view(request):
    """Main journal view with entry form and calendar."""
    form = JournalEntryForm()
    today = timezone.now().date()
    entries = JournalEntry.objects.filter(user=request.user, timestamp__date=today)

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
        .order_by("timestamp__date")  # Ordered chronologically
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

        # Return entries for today (new entries are always for today)
        today = timezone.now().date()
        entries = JournalEntry.objects.filter(user=request.user, timestamp__date=today)
        return render(
            request,
            "journal/partials/entries.html",
            {
                "entries": entries,
                "selected_date": today,
                "entry_saved": True,  # Flag for JS to show success feedback
            },
        )

    # Handle invalid form (though mostly client-side validation handles this)
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
    )

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

    # Capture the date before deleting to return the correct list
    entry_date = entry.timestamp.date()
    target_id = request.GET.get("target", "entries-list")

    entry.delete()

    # Return the updated list for that date
    entries = JournalEntry.objects.filter(user=request.user, timestamp__date=entry_date)

    context = {
        "entries": entries,
        "selected_date": entry_date,
    }

    # If deleting from past entries viewer, include target_id
    if target_id == "past-entries-container":
        context["target_id"] = target_id

    return render(
        request,
        "journal/partials/entries.html",
        context,
    )


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
