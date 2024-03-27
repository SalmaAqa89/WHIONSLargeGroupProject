from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import JournalEntry,Template
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

class TrashViewTests(TestCase):
    
    def setUp(self):
        User = get_user_model()
        
        self.user = User.objects.create_user(username='@testuser', password='Hello12345.')
        self.client.login(username='@testuser', password='Hello12345.')

        
        JournalEntry.objects.create(user=self.user, title="Entry 1", text="Text 1", deleted=True, permanently_deleted=False)
        JournalEntry.objects.create(user=self.user, title="Not Deleted Entry", text="Text 2", deleted=False, permanently_deleted=False)
        JournalEntry.objects.create(user=self.user, title="Search Entry", text="Searchable Text", deleted=True, permanently_deleted=False)

    
    def test_login_required(self):
    
      self.client.logout()
      response = self.client.get(reverse('trash'))  
      expected_url = f"/log_in/?next={reverse('trash')}"
      self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_trash_view_without_search(self):
        response = self.client.get(reverse('trash')) 
        self.assertEqual(response.status_code, 200)


    def test_trash_view_with_search(self):
     expected_entry = JournalEntry.objects.create(
         user=self.user, 
         title="Search Entry", 
         text="Searchable Text", 
         deleted=True, 
         permanently_deleted=False
    )

     response = self.client.post(reverse('trash'), {'search': 'Searchable'})
     self.assertEqual(response.status_code, 200)
     self.assertTrue(expected_entry in response.context['journal_entries'])
