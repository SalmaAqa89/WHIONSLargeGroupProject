"""Unit tests for the Journal Entry model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import JournalEntry

class JournalEntryModelTestCase(TestCase):
    """Unit tests for the Journal Entry model."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_entry.json',
        'tasks/tests/fixtures/other_entries.json',
    ]

    def setUp(self):
        self.entry = JournalEntry.objects.get(title='New Entry')

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

    def test_task_name_cannot_be_over_50_characters_long(self):
        self.entry.title = 'x' * 51
        self._assert_entry_is_invalid()

    def test_task_name_need_not_be_unique(self):
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