from django.test import TestCase
from tasks.tasks import send_reminder_emails, check_and_trigger_reminder_emails
from tasks.models import UserPreferences, User
from datetime import datetime, timedelta
import task_manager.settings as settings
from django.utils import timezone
from unittest.mock import ANY, patch, MagicMock
from tasks.tasks import reset_flower_growth_weekly, check_and_reset_growth_daily
from tasks.models import FlowerGrowth, JournalEntry, User


class TestEmailReminderTasks(TestCase):

    @patch('tasks.tasks.EmailMultiAlternatives.send')
    def test_send_reminder_emails(self, mock_send_mail):
        user_email = 'test@example.com'
        send_reminder_emails(user_email)
        mock_send_mail.assert_called_once()

    @patch('tasks.tasks.send_reminder_emails.apply_async')
    @patch('tasks.tasks.UserPreferences.objects.filter')
    def test_check_and_trigger_reminder_emails(self, mock_filter, mock_apply_async):
        # First test case: User preferences exist for the current day
        mock_preference = UserPreferences(user=User.objects.create(username='testuser'), journal_time=datetime.now().time(), opt_out=False)
        mock_filter.return_value = [mock_preference]
        check_and_trigger_reminder_emails()
        mock_filter.assert_called_once()
        scheduled_time = datetime.combine(datetime.today(), mock_preference.journal_time)
        mock_apply_async.assert_called_once_with(
            args=[mock_preference.user.email],
            eta=scheduled_time,
        )

        # Reset mock objects for the next test case
        mock_filter.reset_mock()
        mock_apply_async.reset_mock()

        # Second test case: No user preferences for the current day
        mock_filter.return_value = []
        check_and_trigger_reminder_emails()
        mock_filter.assert_called_once()
        mock_apply_async.assert_not_called()

        # Reset mock objects for the next test case
        mock_filter.reset_mock()
        mock_apply_async.reset_mock()

class TestFlowerGrowthTasks(TestCase):

    def setUp(self):
        # Assuming this setup method is shared with the test_reset_flower_growth_weekly method above
        self.user1 = User.objects.create(username='user1', email='user1@example.com')
        self.user2 = User.objects.create(username='user2', email='user2@example.com')
        FlowerGrowth.objects.create(user=self.user1, stage=5)
        FlowerGrowth.objects.create(user=self.user2, stage=3)
        JournalEntry.objects.create(user=self.user1, created_at=timezone.now() - timedelta(days=1))

    def test_reset_flower_growth_weekly(self):
        # Execute the weekly reset task
        reset_flower_growth_weekly()

        # Fetch the updated FlowerGrowth instances
        flower_growth_user1 = FlowerGrowth.objects.get(user=self.user1)
        flower_growth_user2 = FlowerGrowth.objects.get(user=self.user2)

        # Check if the stages have been reset to 0
        self.assertEqual(flower_growth_user1.stage, 0)
        self.assertEqual(flower_growth_user2.stage, 0)

        # Check if the last_entry_date is updated to today's date
        self.assertEqual(flower_growth_user1.last_entry_date, timezone.now().date())
        self.assertEqual(flower_growth_user2.last_entry_date, timezone.now().date())

    @patch('tasks.models.FlowerGrowth.objects.exclude')
    @patch('tasks.models.JournalEntry.objects.filter')
    def test_check_and_reset_growth_daily(self, mock_journal_filter, mock_flower_exclude):
        # Mock the JournalEntry filter to return user1, simulating they made an entry yesterday
        mock_journal_filter.return_value.values_list.return_value.distinct.return_value = [self.user1.id]

        mock_exclude = MagicMock()
        mock_flower_exclude.return_value = mock_exclude

        # Execute the daily check and reset task
        check_and_reset_growth_daily()

        # Verify the journal entries filter was called correctly
        mock_journal_filter.assert_called_once_with(created_at__date=timezone.now().date() - timedelta(days=1))
        
        # Verify the correct users are excluded based on the journal entries
        mock_flower_exclude.assert_called_once_with(user__in=[self.user1.id])
        
        # Assert the remaining users have their flower growth stage reset
        mock_exclude.update.assert_called_once_with(stage=0)
    
