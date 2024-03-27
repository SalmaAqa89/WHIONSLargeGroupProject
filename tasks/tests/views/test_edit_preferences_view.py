
from django.test import TestCase
from django.urls import reverse
from tasks.forms import UserPreferenceForm
from tasks.models import UserPreferences, User
from tasks.tests.helpers import LogInTester, reverse_with_next

class EditPreferencesViewTestCase(TestCase, LogInTester):
    """Tests of the edit preferences view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('edit_preferences')
        self.user = User.objects.get(username='@johndoe')

    def test_edit_preferences_url(self):
        self.assertEqual(self.url, '/edit_preferences/')

    def test_get_edit_preferences_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_edit_preferences(self):
        self.client.login(username=self.user.username, password='Password123')
        UserPreferences.objects.create(user=self.user, journal_time='17:30:00')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/edit_preferences.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserPreferenceForm))
        self.assertFalse(form.is_bound)

    def test_edit_preferences_success(self):
        self.client.login(username=self.user.username, password='Password123')
        UserPreferences.objects.create(user=self.user, journal_time='17:30:00')
        form_data = {
            'journal_time': '18:00:00',
            'monday': True,
            'tuesday': False,
            'wednesday': True,
            'thursday': False,
            'friday': True,
            'saturday': False,
            'sunday': False,
        }
        response = self.client.post(self.url, form_data, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'pages/dashboard.html')
        self.assertTrue(UserPreferences.objects.filter(user=self.user, journal_time='18:00:00').exists())

    def test_edit_preferences_form_invalid(self):
        self.client.login(username=self.user.username, password='Password123')
        UserPreferences.objects.create(user=self.user, journal_time='17:30:00')
        form_data = {
            # Incomplete or invalid form data
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/edit_preferences.html')
        self.assertTrue(response.context['form'].errors)
    
    def test_edit_preferences_opt_out(self):

        self.client.login(username=self.user.username, password='Password123')

        UserPreferences.objects.create(user=self.user, journal_time='17:30:00')

        form_data = {
            'journal_time': '18:00:00',
            'opt_out': True,  
            'monday': True,  
            'tuesday': True,
            'wednesday': True,
            'thursday': True,
            'friday': True,
            'saturday': True,
            'sunday': True,
        }

        response = self.client.post(self.url, form_data)

        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        updated_preferences = UserPreferences.objects.get(user=self.user)

        self.assertFalse(updated_preferences.monday)
        self.assertFalse(updated_preferences.tuesday)
        self.assertFalse(updated_preferences.wednesday)
        self.assertFalse(updated_preferences.thursday)
        self.assertFalse(updated_preferences.friday)
        self.assertFalse(updated_preferences.saturday)
        self.assertFalse(updated_preferences.sunday)