from django.test import TestCase
from django.urls import reverse
from tasks.models import JournalEntry, User
from tasks.forms import JournalEntryForm
from tasks.tests.helpers import reverse_with_next

class JournalEntryUpdateViewTestCase(TestCase):
    """Tests for JournalEntryUpdateView."""
    
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username=self.user.username, password='Password123')
        self.journal_entry = JournalEntry.objects.create(user=self.user, title='Test Title', text='Test Text')
        self.url = reverse('edit_entry', kwargs={'pk': self.journal_entry.pk})
        self.form_input = {
            "title": "Updated Title",
            "text": "Updated Text",
            "mood": 3
        }
    
    def test_edit_entry_url(self):
        pk = self.journal_entry.pk
        expected_url = f'/edit/{pk}/'
        self.assertEqual(self.url, expected_url)

    def test_get_edit_journal_entry(self):
        response = self.client.get(reverse('edit_entry', kwargs={'pk': self.journal_entry.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/edit_entry.html')
        form = response.context['form']
        self.assertIsInstance(form, JournalEntryForm)
        self.assertEqual(form.instance, self.journal_entry)
        self.assertEqual(form.instance.user, self.user)

    
    def test_successful_edit_entry(self):
        before_count = JournalEntry.objects.count()
        response = self.client.post(self.url, data=self.form_input, follow=True)
        after_count = JournalEntry.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('journal_log')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'pages/journal_log.html')
        self.journal_entry.refresh_from_db()
        self.assertEqual(self.journal_entry.title, 'Updated Title')
        self.assertEqual(self.journal_entry.text, 'Updated Text')
        self.assertEqual(self.journal_entry.mood, 3)

    def test_unsuccessful_edit_entry(self):
        self.form_input['title'] = ''
        before_count = JournalEntry.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = JournalEntry.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.journal_entry.refresh_from_db()
        self.assertEqual(self.journal_entry.title, 'Test Title')

 