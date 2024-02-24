from django.test import TestCase
from tasks.models import JournalEntry, User
from django.urls import reverse
from tasks.tests.helpers import reverse_with_next


class CreateJounalEntryViewTestCase(TestCase):

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('create_entry')
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            "title": "New entry", 
            "text": "This is a new journal entry",
            "mood": 2
        }

    def test_create_entry_url(self):
        self.assertEqual(self.url,'/create_entry/')

    def test_create_journal_entry_page_content(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Title:", html=True)
        self.assertContains(response, "Text:", html=True)
        self.assertContains(response, "This is the default template", html=True)

    def test_get_create_entry_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_create_task_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_entry(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_entry.html')

    def test_succesful_create_entry(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = JournalEntry.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = JournalEntry.objects.count()
        self.assertEqual(before_count + 1, after_count)
        response_url = reverse('journal_log')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'journal_log.html')
        entry = JournalEntry.objects.get(title='New entry')
        self.assertTrue(entry.text == 'This is a new journal entry')

    def test_unsuccesful_create_entry_with_blank_title(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = JournalEntry.objects.count()
        self.form_input['title'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = JournalEntry.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_entry.html')

    def test_unsuccesful_create_entry_with_blank_text(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = JournalEntry.objects.count()
        self.form_input['text'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = JournalEntry.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_entry.html')
