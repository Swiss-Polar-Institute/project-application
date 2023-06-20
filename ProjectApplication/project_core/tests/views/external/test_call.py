from datetime import datetime

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import utc

from project_core.tests import database_population


class CallFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._client_management = database_population.create_applicant_logged_client()

    def test_list_of_calls(self):
        response = self._client_management.get(reverse('call-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Open calls')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')

    def test_list_of_calls_not_open_yet(self):
        self._call.call_open_date = utc.localize(datetime(2099, 1, 1))
        self._call.save()

        response = self._client_management.get(reverse('call-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Open calls')
        self.assertNotContains(response, 'GreenLAnd Circumnavigation Expedition')
