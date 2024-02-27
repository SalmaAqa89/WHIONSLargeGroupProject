from django.test import TestCase
from django.urls import reverse
from tasks.models import User, JournalEntry

class FavouriteAndUnfavouriteJournalntryViewTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json', 
                'tasks/tests/fixtures/default_entry.json', 'tasks/tests/fixtures/other_entries.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username=self.user.username, password='Password123')
     
        self.not_favourite_entry = JournalEntry.objects.get(pk=1)
        self.favourite_entry = JournalEntry.objects.get(pk=2)
        self.favourite_url = reverse('favourite_entry', kwargs={'entry_id': self.not_favourite_entry.id})
        self.unfavourite_url = reverse('unfavourite_entry', kwargs={'entry_id': self.favourite_entry.id})

    def test_urls(self):
        self.assertEqual(self.favourite_url, f'/favourite_entry/{self.not_favourite_entry.id}')
        self.assertEqual(self.unfavourite_url, f'/unfavourite_entry/{self.favourite_entry.id}')

    def test_favourite_entry(self):
        # Check that the entry is not in favourites
        self.assertFalse(self.not_favourite_entry.favourited)

        # Perform the entry deletion
        response = self.client.get(self.favourite_url)

        entry = JournalEntry.objects.get(pk=self.not_favourite_entry.id)
        
        self.assertTrue(entry.favourited)
        self.assertRedirects(response, reverse('favourites'))

    def test_unfavourite_entry(self):
        # Check that the entry is in favourites
        self.assertTrue(self.favourite_entry.favourited)

        # Perform the entry deletion
        response = self.client.get(self.unfavourite_url)

        entry = JournalEntry.objects.get(pk=self.favourite_entry.id)
        
        self.assertFalse(entry.favourited)
        self.assertRedirects(response, reverse('favourites'))
    