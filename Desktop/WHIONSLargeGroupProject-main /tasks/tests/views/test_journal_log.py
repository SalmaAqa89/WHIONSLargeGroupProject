from django.test import TestCase
from django.urls import reverse
from tasks.models import User

class TestJournalLogTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json', 
                'tasks/tests/fixtures/default_entry.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('journal_log')

    def test_journal_log_url(self):
        self.assertEqual(self.url,'/journal_log/')

    def test_journal_log_page_content(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Entry", html=True)
        self.assertContains(response, "This is a new entry", html=True)

    def test_get_show_empty_journal_log(self):
        self.client.login(username="@peterpickles", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal_log.html')