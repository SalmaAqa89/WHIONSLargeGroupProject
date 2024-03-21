from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from tasks.models import JournalEntry
from django.http import JsonResponse
class FavouriteViewsTest(TestCase):
    def setUp(self):
        
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

       
        JournalEntry.objects.create(title="Favourite Entry 1", user=self.user, deleted=False, favourited=True)
        JournalEntry.objects.create(title="Favourite Entry 2", user=self.user, deleted=False, favourited=False)
        JournalEntry.objects.create(title="Non Favourite Entry", user=self.user, deleted=False, favourited=False)

    def test_search_favourite_view(self):
       
        response = self.client.get(reverse('search_favourite'), {'title': 'Favourite Entry 1'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')
        journal_entries = response.context['journal_entries']
        self.assertEqual(len(journal_entries), 1)
        self.assertEqual(journal_entries[0].title, "Favourite Entry 1")


    def test_search_favouriteSuggestion_view(self):
       
        response = self.client.get(reverse('search_favouriteSuggestion'), {'q': 'Favourite'})
        self.assertEqual(response.status_code, 200)
        suggestions = response.json()['suggestions']
        self.assertTrue("Favourite Entry 1" in suggestions)
       