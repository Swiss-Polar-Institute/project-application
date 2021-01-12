from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class TemplateQuestionTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._question1, self._question2 = database_population.create_template_questions()
        self._client_management = database_population.create_management_logged_client()

    def test_load_template_question_add(self):
        response = self._client_management.get(reverse('logged-template-question-add'))
        self.assertEqual(response.status_code, 200)

    def test_load_template_question_update(self):
        response = self._client_management.get(reverse('logged-template-question-update', kwargs={'pk': self._question1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._question1.question_description)

    def test_load_template_question_detail(self):
        response = self._client_management.get(reverse('logged-template-question-detail', kwargs={'pk': self._question1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._question1.question_description)
