from django.utils import timezone
from datetime import timedelta
from .models import JournalEntry
from django.contrib.auth.decorators import login_required


def add_journal_streak(request):
    if request.user.is_authenticated:
        now = timezone.now()
        all_entries = JournalEntry.objects.filter(user=request.user)
        dates_journaled = {entry.created_at.date() for entry in all_entries}
        streak = 0
        date = now.date()
        while True:
            if date in dates_journaled:
                streak += 1
            elif date != now.date():
                break
            date -= timedelta(days=1)

        return {'journal_streak': streak}
    else:
        return {'journal_streak': 0}

