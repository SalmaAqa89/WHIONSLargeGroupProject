from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import User
from tasks.models import Template

class TemplateChoicesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='pass')
        self.client.login(username='test', password='pass')

    def test_template_choices_get(self):
        # Create some sample templates
        Template.objects.create(name="Template 1")
        Template.objects.create(name="Template 2")

        # Make a GET request to the view
        response = self.client.get(reverse('template_choices'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/template_choices.html')
        self.assertTrue('templates' in response.context)
        self.assertEqual(len(response.context['templates']), 2)  

    def test_template_choices_post(self):
        template = Template.objects.create(name="Test Template")

        # Create a POST request
        data = {'selected_template_name': template.name}
        response = self.client.post(reverse('template_choices'), data)
        self.assertEqual(response.status_code, 302)

        # Check if the session is updated with the selected template name
        self.assertEqual(self.client.session['template_name'], template.name)
        self.assertEqual(response.url, reverse('create_entry'))
