from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tasks.models import User, Template
from freezegun import freeze_time  # Import freezegun if you're manipulating dates

class TemplateChoicesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='@test', password='pass', date_joined=timezone.now() - timedelta(days=10))
        self.client.login(username='@test', password='pass')

    def test_template_choices_get(self):
        Template.objects.create(name="Template 1", unlock_after_days=0,user = self.user)  
        Template.objects.create(name="Template 2", unlock_after_days=5,user = self.user)  
        Template.objects.create(name="Template 3", unlock_after_days=15,user = self.user) 

        # Make a GET request to the view
        response = self.client.get(reverse('template_choices'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/template_choices.html')
        self.assertTrue('templates' in response.context)

        
        self.assertEqual(len(response.context['templates']), 6)

    def test_template_choices_post(self):
        template = Template.objects.create(name="Test Template", unlock_after_days=0,user = self.user)

        
        data = {'selected_template_name': template.name}
        response = self.client.post(reverse('template_choices'), data)
        self.assertEqual(response.status_code, 302)

        # Check if the session is updated with the selected template name
        self.assertEqual(self.client.session['template_name'], template.name)
        self.assertEqual(response.url, reverse('create_entry'))
