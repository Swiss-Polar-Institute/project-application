from datetime import datetime

from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()

    def test_list_of_calls(self):
        c = Client()

        response = c.get(reverse('call-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'List of open calls')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')

    def test_list_of_calls_not_open_yet(self):
        c = Client()

        self._call.call_open_date = datetime(2099, 1, 1)
        self._call.save()

        response = c.get(reverse('call-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'List of open calls')
        self.assertNotContains(response, 'GreenLAnd Circumnavigation Expedition')
