from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallQuestionTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._call_part = database_population.create_call_part(self._call)

        self._call_part_question = database_population.create_call_question(self._call_part)
        self._client_management = database_population.create_management_logged_client()

    def test_details(self):
        response = self._client_management.get(
            reverse('logged-call-part-question-detail', kwargs={'call_pk': self._call.pk,
                                                                'call_question_pk': self._call_part_question.pk
                                                                }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call_part_question.question_text)
