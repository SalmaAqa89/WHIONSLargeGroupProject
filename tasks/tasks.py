import logging
from celery import shared_task
from django.core.mail import send_mail
from .models import UserPreferences
from datetime import datetime

logger = logging.getLogger(__name__)

@shared_task
def send_reminder_emails(user_email):
    logger.info(f"Sending reminder email to {user_email}")
    send_mail(
        'Reminder: Journal Entry',
        'Don\'t forget to make your journal entry today!',
        'hannah.ishimwe@gmail.com',  # Update with your email
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
        logger.info(f"Scheduling reminder email for {preference.user.email} at {scheduled_time}")
        send_reminder_emails.apply_async(args=[preference.user.email], eta=scheduled_time)