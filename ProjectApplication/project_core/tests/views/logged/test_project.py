from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class ProjectListTest(TestCase):
    def test_get(self):
        client = database_population.create_management_logged_client()

        database_population.create_project('TEST-2021-001', 'Test project')

        response = client.get(reverse('logged-project-list'))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'TEST-2021-001')
        self.assertContains(response, 'Test project')
