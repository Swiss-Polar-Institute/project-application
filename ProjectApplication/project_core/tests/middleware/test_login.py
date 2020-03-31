from django.test import TestCase, RequestFactory
from django.urls import reverse

from project_core.middleware.login import LoginRequiredMiddleware
from project_core.tests import database_population


class LoginRequiredMiddlewareTest(TestCase):
    def setUp(self):
        self._middleware_login = LoginRequiredMiddleware()
        self._user_manager = database_population.create_management_user()
        self._user_reviewer = database_population.create_reviewer_user()

    def test_management_can_access(self):
        request = RequestFactory().get(reverse('logged-evaluation-list'))

        request.user = self._user_manager

        response = self._middleware_login.process_request(request)

        self.assertIsNone(response)

    def test_reviewer_cannot_access(self):
        request = RequestFactory().get(reverse('logged-evaluation-list'))

        request.user = self._user_reviewer

        response = self._middleware_login.process_request(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('accounts-login')))

    def test_reviewer_can_access(self):
        request = RequestFactory().get(reverse('logged-proposal-list'))

        request.user = self._user_reviewer

        response = self._middleware_login.process_request(request)

        self.assertIsNone(response)
