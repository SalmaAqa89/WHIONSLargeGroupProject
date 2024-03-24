from django.test import TestCase
from django.urls import reverse
from tasks.models import User, JournalEntry

class DeleteSelectedEntriesTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/default_entry.json']
    
    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username=self.user.username, password='Password123')

        self.entries = JournalEntry.objects.filter(user=self.user)
        self.entry_ids = list(self.entries.values_list('pk', flat=True))
        self.url = reverse('delete_selected_entries')

    def test_delete_selected_entries(self):
        data = {'entryIds': self.entry_ids}
        response = self.client.post(self.url, data, content_type='application/json')

        self.assertTrue(JournalEntry.objects.filter(pk__in=self.entry_ids).exists())

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True, 'message': 'Selected entries moved to trash!'})

