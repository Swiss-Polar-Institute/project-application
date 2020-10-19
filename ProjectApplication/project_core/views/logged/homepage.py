from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from project_core.templatetags.request_is_reviewer import request_is_reviewer


class Homepage(View):
    def get(self, request, *args, **kwargs):

        if request_is_reviewer(request):
            return redirect(reverse('logged-proposal-list'))
        else:
            return redirect(reverse('logged-news'))
