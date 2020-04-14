from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from project_core.templatetags.request_is_reviewer import request_is_reviewer


class Changelog(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if request_is_reviewer(request):
            return HttpResponseRedirect(reverse('logged-proposal-list'))

        context.update({'active_section': 'home',
                        'active_subsection': 'changelog',
                        'sidebar_template': 'logged/_sidebar-home.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Home'}]

        return render(request, 'logged/changelog.tmpl', context)
