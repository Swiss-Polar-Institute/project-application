from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallList(TestCase):
    def setUp(self):
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-changelog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Version deployed')
        self.assertContains(response, 'Changelog')
