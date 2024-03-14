""" Use UnitTest to test the tasks 
    run: python -m unittest tasks.tests.test_tasks"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Initialize Django settings
import django
from django.conf import settings
settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'tasks',
    ],
)

django.setup()

# Import the tasks
from tasks.tasks import send_reminder_emails, check_and_trigger_reminder_emails
import task_manager.settings as settings

class TestCeleryTasks(unittest.TestCase):

    @patch('tasks.tasks.send_mail')
    def test_send_reminder_emails(self, mock_send_mail):
        #going to use the email it should send from as the user email
        user_email = settings.EMAIL_FROM
        send_reminder_emails(user_email)
        mock_send_mail.assert_called_once_with(
            'Reminder: Journal Entry',
            'Don\'t forget to make your journal entry today!',
            settings.EMAIL_FROM,  
            [user_email],
            fail_silently=False,
        )

    @patch('tasks.tasks.send_reminder_emails.apply_async')
    @patch('tasks.tasks.UserPreferences.objects.filter')
    def test_check_and_trigger_reminder_emails(self, mock_filter, mock_apply_async):
        mock_preference = MagicMock()
        mock_preference.user.email = settings.EMAIL_FROM
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