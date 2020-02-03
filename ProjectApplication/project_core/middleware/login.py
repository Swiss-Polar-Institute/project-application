# Partially copied from https://github.com/CleitonDeLima/django-login-required-middleware/blob/master/login_required/middleware.py
# (MIT license)

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredFormanagementMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), (
            'The LoginRequiredMiddleware requires authentication middleware '
            'to be installed. Edit your MIDDLEWARE setting to insert before '
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        if not request.user.is_authenticated and request.path.startswith(settings.LOGIN_REDIRECT_URL):
            return redirect_to_login(request.path)
