from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class ListTest(TestCase):
    def test_get(self):
        client = database_population.create_management_logged_client()

        response = client.get(reverse('logged-lists'))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'List Proposals')
        self.assertContains(response, 'List Projects')
        self.assertContains(response, 'List People')
        self.assertContains(response, 'List Financial keys')
        self.assertContains(response, 'List Users')
