
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from tasks.models import FlowerGrowth, JournalEntry, UserPreferences, User
from tasks.helpers import login_prohibited
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from datetime import datetime, timedelta
from reportlab.lib.enums import TA_CENTER
from datetime import timedelta
from django.urls import reverse



DEFAULT_TEMPLATE = {"name" : "Default template", "text" : "This is the default template"}

@login_required
def dashboard(request):
    if request.user.is_authenticated != True:
        return redirect(reverse('log_in'))
    else:
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


        return render(request, 'pages/dashboard.html', {
            'user': request.user,
            'days_since_account_creation': (now - request.user.created_at).days,
            'days_journaled': len(dates_journaled),
            'journal_streak': streak,
        })

@login_required
def journal_log(request):
    if request.user.is_authenticated != True:
        return redirect(reverse('log_in'))
    else:
        return render(request, 'pages/journal_log.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user)})

@login_required
def favourites(request):
    if request.user.is_authenticated != True:
        return redirect(reverse('log_in'))
    else:
        return render(request, 'pages/favourites.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user, favourited=True)})

@login_required
def templates(request):
    if request.user.is_authenticated != True:
        return redirect(reverse('log_in'))
    else:
        return render(request, 'pages/templates.html', {"templates": [DEFAULT_TEMPLATE]})

@login_required
def trash(request):
    if request.user.is_authenticated != True:
        return redirect(reverse('log_in'))
    else:
        return render(request, 'pages/trash.html',{'journal_entries' : JournalEntry.objects.filter(user=request.user, deleted=True, permanently_deleted=False)})


@login_prohibited
def home(request):
    if request.user.is_authenticated != True:
        return redirect(reverse('log_in'))
    else:
        """Display the application's start/home screen."""

        return render(request, 'pages/home.html')

