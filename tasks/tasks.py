from celery import shared_task
from django.utils import timezone
from .models import FlowerGrowth, JournalEntry

@shared_task
def reset_flower_growth_weekly():
    FlowerGrowth.objects.all().update(stage=0, last_entry_date=timezone.now().date())
    
@shared_task
def check_and_reset_growth_daily():
    today = timezone.now().date()
    users_with_entries_yesterday = JournalEntry.objects.filter(
        created_at__date=today - timezone.timedelta(days=1)
    ).values_list('user', flat=True).distinct()

    FlowerGrowth.objects.exclude(user__in=users_with_entries_yesterday).update(stage=0)