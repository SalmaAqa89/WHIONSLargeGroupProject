from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from tasks.models import JournalEntry 
from PyPDF2 import PdfReader
from io import BytesIO

User = get_user_model()
class ExportTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='@johndoe', password='Password123')
        self.entry = JournalEntry.objects.create(title="Test Entry", text="This is a test.", user=self.user)


    def test_export_journal_entry_to_pdf(self):
        response = self.client.get(reverse('export_journal_entry_to_pdf', args=[self.entry.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        pdf = PdfReader(BytesIO(response.content))
        page = pdf.pages[0]  
        text = page.extract_text()
        self.assertIn('Test Entry', text)
       

    def test_export_journal_entry_to_rtf(self):
        response = self.client.get(reverse('export_journal_entry_to_rtf', args=[self.entry.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rtf')
        self.assertIn('Test Entry', response.content.decode())

    def test_export_entries_invalid_format(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('export_entries'), {'entries': self.entry.id, 'format': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Invalid export format')