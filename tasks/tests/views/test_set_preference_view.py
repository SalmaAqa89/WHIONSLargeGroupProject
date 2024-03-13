"""Tests of the set preferences view."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from tasks.forms import UserPreferenceForm
from tasks.models import UserPreferences, User
from tasks.tests.helpers import LogInTester, reverse_with_next


class SetPreferenceViewTestCase(TestCase, LogInTester):
    """Tests of the set preferences view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('set_preferences')
        self.user = User.objects.get(username='@johndoe')

    def test_set_preference_url(self):
        self.assertEqual(self.url, '/set_preferences/')

    def test_get_set_preference_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_set_preference(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'set_preferences.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserPreferenceForm))
        self.assertFalse(form.is_bound)

    def test_get_set_preference_redirects_when_preferences_exist(self):
        UserPreferences.objects.create(user=self.user, journal_time='17:30:00')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_preference_success(self):
        self.client.login(username=self.user.username, password='Password123')
        form_data = {
            'journal_time': '17:30:00',
            'monday': True,
            'tuesday': True,
            'wednesday': False,
            'thursday': True,
            'friday': False,
            'saturday': False,
            'sunday': False,
        }
        response = self.client.post(self.url, form_data, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertTrue(UserPreferences.objects.filter(user=self.user).exists())