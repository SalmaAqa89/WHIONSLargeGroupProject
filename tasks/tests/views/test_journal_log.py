from django.test import TestCase
from django.urls import reverse
from tasks.models import User

class TestJournalLogTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json', 
                'tasks/tests/fixtures/default_entry.json', 'tasks/tests/fixtures/other_entries.json']

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
        self.assertContains(response, "New Entry 2", html=True)
        self.assertNotContains(response, "New Entry 3", html=True)
        self.assertContains(response, "This is a new entry", html=True)

    def test_get_show_empty_journal_log(self):
        self.client.login(username="@peterpickles", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/journal_log.html')

    def test_search_matching(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'search':'entry 2'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/journal_log.html')
        self.assertContains(response, "New Entry 2")
        self.assertNotContains(response, self.user.username)

    def test_search_not_matching(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'search':'entry 3'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/journal_log.html')
        self.assertNotContains(response, "New Entry 2")
        self.assertNotContains(response, self.user.username)