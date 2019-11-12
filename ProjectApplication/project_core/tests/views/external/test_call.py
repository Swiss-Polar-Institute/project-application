from datetime import datetime

from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.models import Call


class CallFormTest(TestCase):
    def setUp(self):
        Call.objects.get_or_create(long_name='GreenLAnd Circumnavigation Expedition',
                                   call_open_date=datetime(2019, 1, 1), submission_deadline=datetime(2025, 1, 31),
                                   budget_maximum=100_000, other_funding_question=False, proposal_partner_question=True)

    def test_list_of_calls(self):
        c = Client()

        response = c.get(reverse('calls-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'List of open calls')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
