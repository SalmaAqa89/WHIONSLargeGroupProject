from django.test import TestCase
from tasks.models import User, Template
from tasks.forms import TemplateForm
from datetime import datetime



class CreateTemplateEntryFormTestCase(TestCase):


    
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            "name": "New Template", 
            "questions": "sample question",
        }

    def test_form_has_necessary_fields(self):
        form = TemplateForm(user=self.user, data=self.form_input, text="template")
        self.assertIn('name', form.fields)
        self.assertIn('questions', form.fields)

    def test_valid_form(self):
        form = TemplateForm(user=self.user, data=self.form_input, text="template")
        self.assertTrue(form.is_valid())

    def test_name_cannot_be_blank(self):
        self.form_input['name'] = ''
        form = TemplateForm(user=self.user, data=self.form_input, text="template")
        self.assertFalse(form.is_valid())


    def test_form_must_save_correctly(self):
        form = TemplateForm(user=self.user, data=self.form_input, text="template")
        before_count = Template.objects.count()
        form.save()
        after_count = Template.objects.count()
        self.assertEqual(before_count + 1, after_count)
        entry = Template.objects.get(name='New Template')
        self.assertTrue(entry.questions == 'sample question')
    
