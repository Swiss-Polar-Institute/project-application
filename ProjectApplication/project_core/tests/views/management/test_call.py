from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallList(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._user = database_population.create_management_user()

    def test_list_calls(self):
        c = Client()

        login = c.login(username='unittest_management', password='12345')
        self.assertTrue(login)

        response = c.get(reverse('logged-calls-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call.long_name)

    def test_call_view(self):
        c = Client()

        login = c.login(username='unittest_management', password='12345')
        self.assertTrue(login)

        response = c.get(reverse('logged-call-detail', kwargs={'id': self._call.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call.long_name)

    def test_create_call_view(self):
        c = Client()

        login = c.login(username='unittest_management', password='12345')
        self.assertTrue(login)

        response = c.get(reverse('logged-call-update', kwargs={'id': self._call.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call.long_name)
