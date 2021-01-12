from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from project_core.models import CallPart
from project_core.tests import database_population


class CallPartTest(TestCase):
    def setUp(self):
        self._client_management = database_population.create_management_logged_client()

        self._call = database_population.create_call()
        self._call_part = database_population.create_call_part(self._call)

    def test_list(self):
        response = self._client_management.get(reverse('logged-call-part-list', kwargs={'call_pk': self._call.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call_part.title)

    def test_detail(self):
        response = self._client_management.get(reverse('logged-call-part-detail', kwargs={'call_pk': self._call.pk,
                                                                                          'call_part_pk': self._call_part.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call_part.title)

    def test_delete(self):
        call_part, created = CallPart.objects.get_or_create(call=self._call, title='Logistics')
        response = self._client_management.post(reverse('logged-call-part-delete'),
                                                data={'callPartId': call_part.pk, 'callId': self._call.id})

        self.assertEqual(response.status_code, 302)

        self.assertRaises(ObjectDoesNotExist, call_part.refresh_from_db)
