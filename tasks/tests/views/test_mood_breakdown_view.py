"""Tests for the mood_breakdown view."""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from tasks.models import JournalEntry
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class MoodBreakdownViewTest(TestCase):
    """Test suite for the mood_breakdown view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        """Set up conditions before running each test."""
        self.user = User.objects.get(username='@johndoe')  
        self.client.force_login(self.user)  
        self.url = reverse('mood_breakdown')
        
        today = timezone.now()
        this_week = today - timedelta(days=3)
        this_month = today - timedelta(days=20)
        
        JournalEntry.objects.create(user=self.user, created_at=today, mood=5, deleted=False)
        JournalEntry.objects.create(user=self.user, created_at=this_week, mood=3, deleted=False)
        JournalEntry.objects.create(user=self.user, created_at=this_month, mood=1, deleted=False)

    def test_mood_breakdown_url(self):
        """Test the URL of the mood_breakdown view."""
        self.assertEqual(self.url, '/mood_breakdown/')  

    def test_mood_breakdown_access(self):
        """Test access to the mood_breakdown view."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mood_breakdown.html')

    def test_mood_breakdown_context_data(self):
        """Test the context data of the mood_breakdown view."""
        response = self.client.get(self.url)
        self.assertIn('mood_today', response.context)
        self.assertIn('mood_week', response.context)
        self.assertIn('mood_month', response.context)
        self.assertIn('mood_chart', response.context)

    def test_mood_breakdown_redirects_when_not_logged_in(self):
        """Test redirection for unauthenticated access to mood_breakdown view."""
        self.client.logout()
        redirect_url = reverse('log_in') 
        response = self.client.get(self.url)
        self.assertRedirects(response, f'{redirect_url}?next={self.url}', status_code=302, target_status_code=200)



