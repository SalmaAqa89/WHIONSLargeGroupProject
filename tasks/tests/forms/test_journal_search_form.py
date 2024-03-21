# Import necessary modules
from django.test import TestCase
from tasks.forms import JournalSearchForm 

class JournalSearchFormTest(TestCase):
    def test_form_valid_with_title(self):
       
        form_data = {'title': 'Test Journal Title'}
        form = JournalSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valid_without_title(self):
       
        form_data = {}  
        form = JournalSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_title_field_label(self):
        form = JournalSearchForm()
        self.assertTrue(form.fields['title'].label == None or form.fields['title'].label == 'Title')

    