from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class TestUserList(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-user-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._user.username)
        self.assertContains(response, 'Management')


class TestUserDetail(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-user-detail', kwargs={'pk': self._user.pk}))
        self.assertEqual(response, self._user.username)
        self.assertContains(response, self._user.username)
