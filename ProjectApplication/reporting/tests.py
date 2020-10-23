from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class ReportingTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-reporting'))
        self.assertEqual(response.status_code, 200)
