
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import JournalEntry
from tasks.forms import JournalSearchForm
from django.contrib.auth import get_user_model
from django.http import JsonResponse
class JournalViewsTest(TestCase):
    def setUp(self):
        
        User = get_user_model()
    
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='secret')
        JournalEntry.objects.create(user=self.user, title='Entry 1', deleted=False)
        JournalEntry.objects.create(user=self.user, title='Another Entry', deleted=False)
        JournalEntry.objects.create(user=self.user, title='Random Entry', deleted=True)  
        self.client.login(username='testuser', password='secret')

    def test_search_journal_view(self): #passed
        
        response = self.client.get(reverse('search_journal'), {'title': 'Entry'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal_log.html')
        self.assertIsInstance(response.context['form'], JournalSearchForm)
        journal_entries = list(response.context['journal_entries'])
        self.assertContains(response, 'Entry 1')
        response = self.client.get(reverse('search_journal'))
        self.assertEqual(len(response.context['journal_entries']), 2)  
    
    
    def test_journal_entries_view(self): #passed.
        journal_entry = JournalEntry.objects.first() 
        if journal_entry is not None:
         response = self.client.get(reverse('journal_detail', args=[journal_entry.id]))
         self.assertEqual(response.status_code, 200)
         self.assertTemplateUsed(response, 'journal_log.html') 

        else:
         self.fail("No journal entries available to test 'journal_detail' view.")

 
    

