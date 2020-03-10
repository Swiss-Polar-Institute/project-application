from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from project_core.templatetags.request_is_reviewer import request_is_reviewer


class Homepage(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if request_is_reviewer(request):
            return HttpResponseRedirect(reverse('logged-proposals-list'))

        context.update({'active_section': 'home',
                        'active_subsection': 'home',
                        'sidebar_template': 'logged/_sidebar-homepage.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Homepage'}]

        return render(request, 'logged/homepage.tmpl', context)
