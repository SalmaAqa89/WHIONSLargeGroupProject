from venv import logger
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from matplotlib.ticker import MaxNLocator
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, UserPreferenceForm
from tasks.models import FlowerGrowth, JournalEntry, UserPreferences, User
from tasks.helpers import login_prohibited
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from collections import Counter
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, CalendarForm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from tasks.models import JournalEntry
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tasks.helpers import login_prohibited
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from datetime import timedelta
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, CalendarForm
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from datetime import datetime, timedelta
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from reportlab.lib.enums import TA_CENTER
from datetime import timedelta



DEFAULT_TEMPLATE = {"name" : "Default template", "text" : "This is the default template"}

@login_required
def dashboard(request):
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


    return render(request, 'dashboard.html', {
        'user': request.user,
        'days_since_account_creation': (now - request.user.created_at).days,
        'days_journaled': len(dates_journaled),
        'journal_streak': streak,
    })

@login_required
def journal_log(request):
    return render(request, 'journal_log.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user)})

@login_required
def favourites(request):
    return render(request, 'favourites.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user, favourited=True)})

@login_required
def templates(request):
    return render(request, 'templates.html', {"templates": [DEFAULT_TEMPLATE]})

@login_required
def trash(request):
    return render(request, 'trash.html',{'journal_entries' : JournalEntry.objects.filter(user=request.user, deleted=True, permanently_deleted=False)})

@login_required
def mood_breakdown(request):
    return render(request, 'mood_breakdown.html')


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

