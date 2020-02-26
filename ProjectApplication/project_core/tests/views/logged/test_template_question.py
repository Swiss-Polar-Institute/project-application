from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class CallList(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._question1, self._question2 = database_population.create_template_questions()

    def test_load_template_question_add(self):
        c = Client()

        login = c.login(username='unittest_management', password='12345')
        self.assertTrue(login)

        response = c.get(reverse('template-question-add'))
        self.assertEqual(response.status_code, 200)

    def test_load_template_question_update(self):
        c = Client()

        login = c.login(username='unittest_management', password='12345')
        self.assertTrue(login)

        response = c.get(reverse('template-question-update', kwargs={'pk': self._question1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._question1.question_description)

    def test_load_template_question_detail(self):
        c = Client()

        login = c.login(username='unittest_management', password='12345')
        self.assertTrue(login)

        response = c.get(reverse('template-question-detail', kwargs={'pk': self._question1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._question1.question_description)

