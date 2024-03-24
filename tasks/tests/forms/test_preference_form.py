"""Unit tests of the preference form."""
from django import forms
from django.test import TestCase
from tasks.forms import UserPreferenceForm
from tasks.models import User, UserPreferences
import datetime

class UserPreferenceFormTestCase(TestCase):
    """Unit tests of the User Preference form."""
    
    fixtures = [
        'tasks/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'journal_time': '17:30:00',
            'monday': 'True',
            'tuesday': 'True',
            'wednesday': 'False',
            'thursday': 'True',
            'friday': 'False',
            'saturday': 'False',
            'sunday': 'False',
            'opt_out': 'False'
        }
        self.user = User.objects.get(username='@johndoe')
        self.days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
    
    def test_valid_preference_form(self):
        form = UserPreferenceForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = UserPreferenceForm()
        self.assertIn('journal_time', form.fields)
        for day in self.days:
            self.assertIn(day, form.fields)
            day_field = form.fields[day]
            self.assertTrue(isinstance(day_field, forms.BooleanField))
            day_widget = day_field.widget
            self.assertTrue(isinstance(day_widget, forms.CheckboxInput))  
        self.assertIn('opt_out', form.fields)  


    def test_journal_time_must_be_time(self):
        self.form_input['journal_time'] = '17'
        form = UserPreferenceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = UserPreferenceForm(data=self.form_input)
        form.instance.user = self.user
        before_count = UserPreferences.objects.count()
        form.save()
        after_count = UserPreferences.objects.count()
        self.assertEqual(after_count, before_count+1)
        pref = UserPreferences.objects.get(user=1)
        self.assertEqual(pref.journal_time, datetime.time(17, 30))
        for day in ['monday', 'tuesday', 'thursday']:
            self.assertTrue(getattr(pref, day))
        for day in ['wednesday', 'friday', 'saturday', 'sunday']:
            self.assertFalse(getattr(pref, day))
        self.assertFalse(getattr(pref, 'opt_out'))
    
    def test_form_must_update_correctly(self):
        form = UserPreferenceForm(data=self.form_input)
        form.instance.user = self.user
        form.save()
        before_count = UserPreferences.objects.count()
        pref = UserPreferences.objects.get(user=1)
        self.form_input['journal_time'] = '18:30:00'
        self.form_input['monday'] = 'False'
        form = UserPreferenceForm(data=self.form_input, instance=pref)
        form.save()
        after_count = UserPreferences.objects.count()
        self.assertEqual(after_count, before_count)
        pref = UserPreferences.objects.get(user=1)
        self.assertEqual(pref.journal_time, datetime.time(18, 30))
        for day in ['tuesday', 'thursday']:
            self.assertTrue(getattr(pref, day))
        for day in ['monday', 'wednesday', 'friday', 'saturday', 'sunday']:
            self.assertFalse(getattr(pref, day))
    

  
