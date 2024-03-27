from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from tasks.models import Template,User
from datetime import timedelta

class TemplateViewTests(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json']
    def setUp(self):
      
        self.user = User.objects.create_user(username='@testuser', password='12345')
        Template.objects.create(name='Template 1', unlock_after_days=0)  # Should be unlocked immediately
        Template.objects.create(name='Template 2', unlock_after_days=5)  # Should be locked for 5 days
        self.client.login(username='@testuser', password='12345')
    
    def test_templates_view_with_authenticated_user(self):
        response = self.client.get(reverse('templates'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('templates' in response.context)
        templates = response.context['templates']
        for template in templates:
            if template.unlock_after_days == 0:
                self.assertFalse(template.is_locked)
            else:
                self.assertTrue(template.is_locked)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('templates'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/log_in/' in response.url) 