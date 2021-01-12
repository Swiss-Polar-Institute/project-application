from django.http import HttpRequest
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallListTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._funding_instrument = database_population.create_funding_instrument()
        self._client_management = database_population.create_management_logged_client()

    def test_load_funding_instrument_add(self):
        login = self._client_management.login(username='unittest_management', password='12345', request=HttpRequest())
        self.assertTrue(login)

        response = self._client_management.get(reverse('logged-funding-instrument-add'))
        self.assertEqual(response.status_code, 200)

    def test_load_funding_instruments_list(self):
        response = self._client_management.get(reverse('logged-funding-instrument-list'))
        self.assertEqual(response.status_code, 200)

    def test_load_funding_instrument_update_get(self):
        response = self._client_management.get(reverse('logged-funding-instrument-update', kwargs={'pk': self._funding_instrument.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._funding_instrument.long_name)

    def test_load_funding_instrument_detail(self):
        response = self._client_management.get(reverse('logged-funding-instrument-detail', kwargs={'pk': self._funding_instrument.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._funding_instrument.long_name)
