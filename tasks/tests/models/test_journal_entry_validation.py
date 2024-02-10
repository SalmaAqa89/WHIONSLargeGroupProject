from django.test import TestCase
from django.core.exceptions import ValidationError
from tasks.models import JournalEntry,User



class JournalEntryValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_valid_journal_entry(self):
        entry = JournalEntry(
            user=self.user,
            title='Valid Entry',
            text='Valid Text',
            deleted=False
        )

        try:
            self.assertTrue(entry.full_clean())
        except(ValidationError):
            self.fail('Journal Entry should be valid')

    def test_invalid_journal_entry_missing_title(self):
        entry = JournalEntry(
            user=self.user,
            text='Invalid Text',
            deleted=False
        )
        with self.assertRaises(ValueError):
            entry.full_clean()

    def test_invalid_journal_entry_empty_title(self):

        entry = JournalEntry(
            user=self.user,
            title='',
            text='Invalid Text',
            deleted=False
        )
        with self.assertRaises(ValueError):
            entry.full_clean()

    def test_invalid_journal_entry_missing_user(self):
        entry = JournalEntry(
            title='Invalid Entry',
            text='Invalid Text',
            deleted=False
        )

        with self.assertRaises(ValueError):
            entry.full_clean()

