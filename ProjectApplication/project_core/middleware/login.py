# Partially copied from https://github.com/CleitonDeLima/django-login-required-middleware/blob/master/login_required/middleware.py
# (MIT license)

from django.contrib.auth.views import redirect_to_login
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredForInternalMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), (
            'The LoginRequiredMiddleware requires authentication middleware '
            'to be installed. Edit your MIDDLEWARE setting to insert before '
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        path = request.path.lstrip('/')
        if not request.user.is_authenticated and path.startswith('internal/'):
            return redirect_to_login(request.path)
