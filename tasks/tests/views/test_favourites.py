from django.test import TestCase
from django.urls import reverse
from tasks.models import User

class TestFavouritesTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json', 
                'tasks/tests/fixtures/default_entry.json', 'tasks/tests/fixtures/other_entries.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('favourites')

    def test_favouritesurl(self):
        self.assertEqual(self.url,'/favourites/')

    def test_favourites_page_content(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "New Entry", html=True)
        self.assertContains(response, "New Entry 2", html=True)
        self.assertContains(response, "This is a new entry", html=True)

    def test_get_show_empty_favourites(self):
        self.client.login(username="@peterpickles", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')