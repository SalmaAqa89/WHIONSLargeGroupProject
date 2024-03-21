
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
from django.db.models import F





DEFAULT_TEMPLATE = {"name" : "Default template", "text" : "This is the default template"}

@login_required
def dashboard(request):
        try:
            stage = request.user.flowergrowth.stage
        except FlowerGrowth.DoesNotExist:
            stage = 0
        flower_image_url = get_flower_stage_image(stage) 

        return render(request, 'pages/dashboard.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user),
                                                        'flower_image_url' : flower_image_url,})


@login_required
def journal_log(request):
    start_date = timezone.now() - timedelta(days=30)
    end_date = timezone.now()

    journal_entries_last_thirty_days = JournalEntry.objects.filter(user=request.user, created_at__range=(start_date, end_date))
    return render(request, 'pages/journal_log.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user),
                                                      'journal_entries_last_thirty_days' : journal_entries_last_thirty_days,})

@login_required
def favourites(request):
    return render(request, 'pages/favourites.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user, favourited=True)})

@login_required
def templates(request):
    return render(request, 'pages/templates.html', {"templates": [DEFAULT_TEMPLATE]})

@login_required
def trash(request):
    return render(request, 'pages/trash.html',{'journal_entries' : JournalEntry.objects.filter(user=request.user, deleted=True, permanently_deleted=False)})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'pages/home.html')


def get_flower_stage_image(stage):
    image_dict = {
        0: 'images/flower_stage_0.png',
        1: 'images/flower_stage_1.png',
        2: 'images/flower_stage_2.png',
        3: 'images/flower_stage_3.png',
        4: 'images/flower_stage_4.png',
        5: 'images/flower_stage_5.png',
        6: 'images/flower_stage_6.png',
        7: 'images/flower_stage_7.png',
    }
    return image_dict.get(stage, 'images/flower_stage_0.png')