""" Contains tasks that will be scheduled by Celery 
Will send out reminder emails based on user preferences 
To run:
    redis-server
    celery -A task_manager worker -l info
    celery -A task_manager beat -l info
"""

from celery import shared_task
from django.core.mail import send_mail
from .models import UserPreferences
from datetime import datetime
import task_manager.settings as settings



@shared_task
def send_reminder_emails(user_email):
    send_mail(
        'Reminder: Journal Entry',
        'Don\'t forget to make your journal entry today!',
        settings.EMAIL_FROM, 
        [user_email],
        fail_silently=False,
    )

@shared_task
def check_and_trigger_reminder_emails():
    # Get today's day of the week
    today = datetime.now().strftime('%A').lower()

    # Get user preferences for the current day
    user_preferences = UserPreferences.objects.filter(**{f"{today}": True})
    
    # Trigger reminders for users who have selected the current day
    for preference in user_preferences:
        scheduled_time = datetime.combine(datetime.today(), preference.journal_time)
        send_reminder_emails.apply_async(args=[preference.user.email], eta=scheduled_time)

