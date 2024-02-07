from django.test import TestCase
from django.urls import reverse
from tasks.models import User, JournalEntry

class DeleteJournalntryViewTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/default_entry.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username=self.user.username, password='Password123')
     
        self.entry = JournalEntry.objects.get(pk=1)
        self.url = reverse('delete_entry', kwargs={'entry_id': self.entry.id})

    def test_get_delete_entry_url(self):
        self.assertEqual(self.url, f'/delete_entry/{self.entry.id}')

    def test_delete_entry(self):
        # Check that the entry exists before deletion
        self.assertTrue(JournalEntry.objects.filter(pk=self.entry.id).exists())

        # Perform the entry deletion
        response = self.client.get(self.url)

        # Check that the entry no longer exists
        with self.assertRaises(JournalEntry.DoesNotExist):
            JournalEntry.objects.get(pk=self.entry.id)

        self.assertRedirects(response, reverse('journal_log'))
    