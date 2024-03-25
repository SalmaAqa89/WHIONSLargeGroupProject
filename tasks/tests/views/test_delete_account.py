from django.test import TestCase
from django.urls import reverse
from tasks.models import User


class AccountDeletionTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='@johndoe', email='johndoe@example.com', password='Password123')
        self.client.login(username=self.user.username, password='Password123')


   
    def test_account_deletion(self):
        # Get the delete account URL
        delete_account_url = reverse('delete_account')
        # Send a POST request to delete the account
        response = self.client.post(delete_account_url)
        # Check that the account has been deleted
        self.assertEqual(response.status_code, 302)  # Expecting a redirect status code
        self.assertFalse(User.objects.filter(username='testuser').exists())  # Check that the user does not exist anymore
