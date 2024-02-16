"""Unit tests of the preference form."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from tasks.forms import UserPreferenceForm
from tasks.models import User, UserPreferences

class SignUpFormTestCase(TestCase):
    """Unit tests of the sign up form."""
    
    fixtures = [
        'tasks/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'journal_time': '17:30:00',
            'number_of_times_to_journal': '3',
            'monday': 'True',
            'tuesday': 'True',
            'wednesday': 'False',
            'thursday': 'True',
            'friday': 'False',
            'saturday': 'False',
            'sunday': 'False',
        }
        self.user = User.objects.get(username='@johndoe')
        self.days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
    
    def set_up(self):
        pass

    def test_valid_sign_up_form(self):
        form = UserPreferenceForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = UserPreferenceForm()
        self.assertIn('journal_time', form.fields)
        self.assertIn('number_of_times_to_journal', form.fields)
        for day in self.days:
            self.assertIn(day, form.fields)
            day_field = form.fields[day]
            self.assertTrue(isinstance(day_field, forms.BooleanField))
            day_widget = day_field.widget
            self.assertTrue(isinstance(day_widget, forms.CheckboxInput))    

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = UserPreferenceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = UserPreferenceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = UserPreferenceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = UserPreferenceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = UserPreferenceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = UserPreferenceForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)