# Partially copied from https://github.com/CleitonDeLima/django-login-required-middleware/blob/master/login_required/middleware.py
# (MIT license)

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils.deprecation import MiddlewareMixin

from project_core.utils.utils import user_is_in_group_name


class LoginRequiredFormanagementMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), (
            'The LoginRequiredMiddleware requires authentication middleware '
            'to be installed. Edit your MIDDLEWARE setting to insert before '
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        if request.path.startswith(settings.LOGIN_REDIRECT_URL):
            if user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
                # Managers can see everything
                return
            elif user_is_in_group_name(request.user, settings.REVIEWER_GROUP_NAME):
                # TODO: change this approach and/or add unit test
                if request.path.startswith('/logged/proposal/') or request.path.startswith('/logged/proposals/') or \
                        request.path == '/logged/':
                    return

            return redirect_to_login(request.path)
