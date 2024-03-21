from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import JournalEntry
from django.contrib.auth import get_user_model
class JournalEntryViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    
        JournalEntry.objects.create(title="Test Entry 1", deleted=True, user=self.user)
  
        JournalEntry.objects.create(title="Deleted Entry", deleted=True, user=self.user)

    def test_search_trash(self):
        response = self.client.get(reverse('search_trash'), {'title': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Entry 1")
        self.assertNotContains(response, "Another Entry")  
        self.assertNotContains(response, "Deleted Entry")  


    def test_search_suggestions1(self):
       
        self.assertTrue(self.client.login(username='testuser', password='12345'))

     
        response = self.client.get(reverse('search-suggestions1'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        

       
        
      
