# Partially copied from https://github.com/CleitonDeLima/django-login-required-middleware/blob/master/login_required/middleware.py
# (MIT license)

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import resolve, reverse, NoReverseMatch
from django.utils.deprecation import MiddlewareMixin

from project_core.utils.utils import user_is_in_group_name


class LoginRequiredMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        LoginRequiredMiddleware._check_view_names_exist()

    @staticmethod
    def _check_view_names_exist():
        """ The application will not start if a settings.REVIEW_CAN_ACCESS_VIEW_NAMES does not exist"""
        for view_name in settings.REVIEWER_CAN_ACCESS_VIEW_NAMES:
            try:
                reverse(view_name)
            except NoReverseMatch as e:
                assert 'with no arguments not found' in str(e), f'view_name: "{view_name}" needs to exist'

    @staticmethod
    def _reviewer_can_access(path):
        resolved_path = resolve(path)

        return resolved_path.url_name in settings.REVIEWER_CAN_ACCESS_VIEW_NAMES

    @staticmethod
    def _applicant_can_access(path):
        resolved_path = resolve(path)

        return resolved_path.url_name in settings.APPLICANT_CAN_ACCESS_VIEW_NAMES

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
                if LoginRequiredMiddleware._reviewer_can_access(request.path):
                    return

            return redirect_to_login(request.path)

        if request.path.startswith(settings.LOGIN_REDIRECT_URL_APPLICANT):
            if user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
                # Managers can see everything
                return
            elif user_is_in_group_name(request.user, settings.APPLICANT_GROUP_NAME):
                if LoginRequiredMiddleware._applicant_can_access(request.path):
                    return
            return redirect_to_login(request.path, login_url='applicant-login')
