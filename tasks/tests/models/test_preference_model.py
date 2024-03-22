from django.test import TestCase
from django.db.utils import IntegrityError
from tasks.models import User, UserPreferences

class UserPreferenceModel(TestCase):
    """Unit Tests for the Journal Entry Model"""
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.preference = UserPreferences.objects.create(
            user=self.user,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=False,
            friday=False,
            saturday=False,
            sunday=False,
            opt_out=False,
            journal_time='17:30:00'
        )



    def test_valid_user_preference(self):
        self.assertTrue(self.preference.monday)
        self.assertTrue(self.preference.tuesday)
        self.assertTrue(self.preference.wednesday)
        self.assertFalse(self.preference.thursday)
        self.assertFalse(self.preference.friday)
        self.assertFalse(self.preference.saturday)
        self.assertFalse(self.preference.sunday)
        self.assertFalse(self.preference.opt_out)
        self.assertEqual(self.preference.journal_time, '17:30:00')
    
    def test_user_preference_must_have_user(self):
        with self.assertRaises(IntegrityError):
            UserPreferences.objects.create(
                monday=True,
                tuesday=True,
                wednesday=True,
                thursday=False,
                friday=False,
                saturday=False,
                sunday=False,
                journal_time='17:30:00'
            )
    def test_user_preference_must_have_only_one_user(self):
        with self.assertRaises(IntegrityError):
            UserPreferences.objects.create(
                user=self.user,
                monday=True,
                tuesday=True,
                wednesday=True,
                thursday=False,
                friday=True,
                saturday=False,
                sunday=False,
                journal_time='17:30:00'
            )
    
    def test_user_preference_must_have_journal_time(self):
        with self.assertRaises(IntegrityError):
            UserPreferences.objects.create(
                user=self.user,
                monday=True,
                tuesday=True,
                wednesday=True,
                thursday=False,
                friday=False,
                saturday=False,
                sunday=False,
            )
    
