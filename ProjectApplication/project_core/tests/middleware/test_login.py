from django.test import TestCase

from project_core.middleware.login import LoginRequiredFormanagementMiddleware


class LoginRequiredFormanagementMiddlewareTest(TestCase):
    def setUp(self):
        self._middleware_login = LoginRequiredFormanagementMiddleware()

    def test_management_access(self):
        print(self._middleware_login)
