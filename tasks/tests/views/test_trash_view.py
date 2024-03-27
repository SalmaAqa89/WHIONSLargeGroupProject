from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from tasks.models import JournalEntry, User,Template
from tasks.forms import JournalEntryForm
from tasks.tests.helpers import reverse_with_next

class TrashViewTestCase(TestCase):
    """Tests for Trash View."""
    
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.journal_entry = JournalEntry.objects.create(user=self.user, title='Test Title', text='Test Text', deleted=True)
        self.template = Template.objects.create( name='Test Template', questions='Test Q', deleted=True,user = self.user)
        self.url = reverse('trash')
    
    def test_trash_url(self):
        expected_url = f'/trash/'
        self.assertEqual(self.url, expected_url)

    def test_get_trash(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('trash'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/trash.html')
        self.assertContains(response, f'<h5 class="card-title">{self.journal_entry.title}</h5>', html=True)
        self.assertContains(response, f'<h5 class="card-title">{self.template.name}</h5>', html=True)

    


    
    def test_successful_recover_entry(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('trash'))
        self.assertContains(response, f'<h5 class="card-title">{self.journal_entry.title}</h5>', html=True)
        recover_response = self.client.get(reverse('recover_entry', args=[self.journal_entry.pk]))
        self.assertEqual(recover_response.status_code, 302)  
        response_after_recovery = self.client.get(reverse('trash'))
        self.assertEqual(response_after_recovery.status_code, 200)
        self.assertNotContains(response_after_recovery, f'<h5 class="card-title">{self.journal_entry.title}</h5>', html=True)
        entry_exists = JournalEntry.objects.filter(pk=self.journal_entry.pk).exists()
        self.assertTrue(entry_exists, "Entry does not exist in the database")

    def test_successful_delete_entry_permanent(self):
        self.client.login(username=self.user.username, password='Password123')
        journal_entry2 = JournalEntry.objects.create(user=self.user, title='Test Title 2', text='Test Text 2', deleted=True)
        response = self.client.get(reverse('trash'))
        self.assertContains(response, f'<h5 class="card-title">{journal_entry2.title}</h5>', html=True)
        recover_response = self.client.get(reverse('delete_entry_permanent', args=[journal_entry2.pk]))
        self.assertEqual(recover_response.status_code, 302)  
        response_after_recovery = self.client.get(reverse('trash'))
        self.assertEqual(response_after_recovery.status_code, 200)
        self.assertNotContains(response_after_recovery, f'<h5 class="card-title">{journal_entry2.title}</h5>', html=True)
        entry_exists = JournalEntry.objects.filter(pk=journal_entry2.pk)
        self.assertFalse(entry_exists, "Entry does exist in the database")
        
    def test_successful_recover_template(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('trash'))
        self.assertContains(response, f'<h5 class="card-title">{self.template.name}</h5>', html=True)
        recover_response = self.client.get(reverse('recover_template', args=[self.template.pk]))
        self.assertEqual(recover_response.status_code, 302)  
        response_after_recovery = self.client.get(reverse('trash'))
        self.assertEqual(response_after_recovery.status_code, 200)
        self.assertNotContains(response_after_recovery, f'<h5 class="card-title">{self.template.name}</h5>', html=True)
        entry_exists = Template.objects.filter(pk=self.template.pk).exists()
        self.assertTrue(entry_exists, "Template does not exist in the database")

    def test_successful_delete_template_permanent(self):
        self.client.login(username=self.user.username, password='Password123')
        template2 = Template.objects.create(name='Test Name 2', questions='Test Questions', deleted=True,user = self.user)
        response = self.client.get(reverse('trash'))
        self.assertContains(response, f'<h5 class="card-title">{template2.name}</h5>', html=True)
        recover_response = self.client.get(reverse('delete_template_permanent', args=[template2.pk]))
        self.assertEqual(recover_response.status_code, 302)  
        response_after_recovery = self.client.get(reverse('trash'))
        self.assertEqual(response_after_recovery.status_code, 200)
        self.assertNotContains(response_after_recovery, f'<h5 class="card-title">{template2.name}</h5>', html=True)
        entry_exists = Template.objects.filter(pk=template2.pk)
        self.assertFalse(entry_exists, "Entry does exist in the database")



    # def test_unsuccessful_edit_entry(self):
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.form_input['title'] = ''
    #     before_count = JournalEntry.objects.count()
    #     response = self.client.post(self.url, self.form_input)
    #     after_count = JournalEntry.objects.count()
    #     self.assertEqual(after_count, before_count)
    #     self.assertEqual(response.status_code, 200)
    #     self.journal_entry.refresh_from_db()
    #     self.assertEqual(self.journal_entry.title, 'Test Title')

 
