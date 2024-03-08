import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from tasks.tasks import send_reminder_emails, check_and_trigger_reminder_emails

class TestCeleryTasks(unittest.TestCase):

    @patch('tasks.tasks.send_mail')
    def test_send_reminder_emails(self, mock_send_mail):
        user_email = 'hannah.ishimwe@gmail.com'
        send_reminder_emails(user_email)
        mock_send_mail.assert_called_once_with(
            'Reminder: Journal Entry',
            'Don\'t forget to make your journal entry today!',
            'hannah.ishimwe@gmail.com',  
            [user_email],
            fail_silently=False,
        )

    @patch('tasks.tasks.send_reminder_emails.apply_async')
    @patch('tasks.tasks.UserPreferences.objects.filter')
    def test_check_and_trigger_reminder_emails(self, mock_filter, mock_apply_async):
        mock_preference = MagicMock()
        mock_preference.user.email = 'hannah.ishimwe@gmail.com'
        mock_preference.journal_time = datetime.now().time().replace(second=0, microsecond=0)
        mock_filter.return_value = [mock_preference]
        check_and_trigger_reminder_emails()
        mock_filter.assert_called_once()

        scheduled_time = datetime.combine(datetime.today(), mock_preference.journal_time)
        mock_apply_async.assert_called_once_with(
            args=[mock_preference.user.email],
            eta=scheduled_time,
        )

if __name__ == '__main__':
    unittest.main()