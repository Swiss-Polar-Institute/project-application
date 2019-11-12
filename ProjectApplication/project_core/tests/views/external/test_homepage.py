from django.test import Client
from django.test import TestCase


class CallFormTest(TestCase):
    def setUp(self):
        pass

    def test_homepage(self):
        c = Client()

        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'List of calls')
