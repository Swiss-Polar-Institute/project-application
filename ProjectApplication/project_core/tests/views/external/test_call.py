from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallFormTest(TestCase):
    def setUp(self):
        database_population.create_call()

    def test_list_of_calls(self):
        c = Client()

        response = c.get(reverse('calls-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'List of open calls')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
