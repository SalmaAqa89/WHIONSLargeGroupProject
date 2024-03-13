"""Tests of the home view."""
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from tasks.models import JournalEntry, User
from tasks.tests.helpers import reverse_with_next

class DashboardViewTestCase(TestCase):
    """Tests of the home view."""

    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json',]

    def setUp(self):
        self.url = reverse('dashboard')
        self.user = User.objects.get(username='@johndoe')

    def test_home_url(self):
        self.assertEqual(self.url,'/dashboard/')

    def test_get_home(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_journal_streak_no_journals(self):
        JournalEntry.objects.create(title="New Entry", text="Text", user=User.objects.get(pk=2))
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, "Number of days Journaled: 0", html=True)
        self.assertContains(response, "Journal Streak Days: 0", html=True)
        
    def test_journal_streak_5_journals(self):
        self.client.login(username=self.user.username, password='Password123')
        for i in range(5):
            entry = JournalEntry.objects.create(title="New Entry", text="Text", user=self.user)
            entry.created_at -= timedelta(days=i)
            entry.save()
        response = self.client.get(self.url)
        self.assertContains(response, "Number of days Journaled: 5", html=True)
        self.assertContains(response, "Journal Streak Days: 5", html=True)

    
    def test_journal_streak_broken(self):
        self.client.login(username=self.user.username, password='Password123')
        for i in range(5):
            if i != 2:
                entry = JournalEntry.objects.create(title="New Entry", text="Text", user=self.user)
                entry.created_at -= timedelta(days=i)
                entry.save()
        response = self.client.get(self.url)
        self.assertContains(response, "Number of days Journaled: 4", html=True)
        self.assertContains(response, "Journal Streak Days: 2", html=True)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)