from django.test import Client
from django.test import TestCase
from django.urls import reverse


class CallFormTest(TestCase):
    def setUp(self):
        pass

    def test_homepage(self):
        c = Client()

        response = c.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'List of calls')
