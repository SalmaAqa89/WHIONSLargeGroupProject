"""Unit tests for the Journal Entry model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import JournalEntry, User

class JournalEntryModelTestCase(TestCase):
    """Unit tests for the Journal Entry model."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_entry.json',
        'tasks/tests/fixtures/other_entries.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.entry = self.entry = JournalEntry.objects.create(
            user=self.user,
            title='Test Entry',
            text='Test Text',
            deleted=False
        )

    def test_valid_entry(self):
        self._assert_entry_is_valid()

    def test_title_cannot_be_blank(self):
        self.entry.title = ''
        self._assert_entry_is_invalid()

    def test_text_cannot_be_blank(self):
        self.entry.text = ''
        self._assert_entry_is_invalid()

    def test_title_can_be_50_characters_long(self):
        self.entry.title  = 'x' * 50
        self._assert_entry_is_valid()

    def test_title_cannot_be_over_50_characters_long(self):
        self.entry.title = 'x' * 51
        self._assert_entry_is_invalid()

    def test_title_need_not_be_unique(self):
        second_entry = JournalEntry.objects.get(title='New Entry 2')
        self.entry.title = second_entry.title
        self._assert_entry_is_valid()

    def test_text_need_not_be_unique(self):
        second_entry = JournalEntry.objects.get(title='New Entry 2')
        self.entry.text = second_entry.title
        self._assert_entry_is_valid()


    def test_different_entries_can_come_from_same_user(self):
        second_entry = JournalEntry.objects.get(title='New Entry 2')
        self.assertEqual(self.entry.user, second_entry.user)

    def test_different_entries_can_come_from_different_user(self):
        second_entry = JournalEntry.objects.get(title='New Entry 3')
        self.assertNotEqual(self.entry.user, second_entry.user)

    def test_get_user_from_entry(self):
        user = self.entry.user
        self.assertEqual(user.username, "@johndoe")

    def test_entry_user_cannot_be_none(self):
        self.entry.user= None
        self._assert_entry_is_invalid()


    def _assert_entry_is_valid(self):
        try:
            self.entry.full_clean()
        except (ValidationError):
            self.fail('Test entry should be valid')

    def _assert_entry_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.entry.full_clean()

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
