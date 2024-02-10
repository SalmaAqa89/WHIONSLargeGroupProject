from django.test import TestCase
from django.core.exceptions import ValidationError
from tasks.models import JournalEntry,User

class JournalEntryModel(TestCase):
    """Unit Tests for the Journal Entry Model"""
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.entry = JournalEntry.objects.create(
            user=self.user,
            title='Test Entry',
            text='Test Text',
            deleted=False
        )

    def test_journal_entry_creation_with_mood(self):
        """Test creating a journal entry with a specific mood"""
        entry = JournalEntry.objects.create(
            user=self.user,
            title='Mood Entry',
            text='Testing moods',
            mood=5  # Very happy mood
        )
        self.assertEqual(entry.mood, 5)

    def test_delete_entry(self):
        self.entry.delete_entry()
        updated_entry = JournalEntry.objects.get(pk=self.entry.pk)
        self.assertTrue(updated_entry.deleted)

    def test_recover_entry(self):
        self.entry.deleted = True
        self.entry.save()
        self.entry.recover_entry()
        updated_entry = JournalEntry.objects.get(pk=self.entry.pk)
        self.assertFalse(updated_entry.deleted)
    
    def test_default_mood_value(self):
        """Test that the default mood value is applied correctly"""
        default_mood_entry = JournalEntry.objects.create(
            user=self.user,
            title='Default Mood Entry',
            text='Text without specifying mood'
        )
        self.assertEqual(default_mood_entry.mood, 3)