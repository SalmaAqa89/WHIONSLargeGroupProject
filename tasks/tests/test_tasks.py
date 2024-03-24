from django.test import TestCase
from unittest.mock import patch
from tasks.tasks import send_reminder_emails, check_and_trigger_reminder_emails
from tasks.models import UserPreferences, User
from datetime import datetime, timedelta
import task_manager.settings as settings


class TestCeleryTasks(TestCase):

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
