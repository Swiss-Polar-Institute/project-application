from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from project_core.templatetags.request_is_reviewer import request_is_reviewer


def get_notable_events():
    return [{'date': datetime.today(), 'description': mark_safe('<strong>TODAY</strong>')}]


class News(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if request_is_reviewer(request):
            return HttpResponseRedirect(reverse('logged-proposal-list'))

        context.update({'active_section': 'home',
                        'active_subsection': 'news',
                        'sidebar_template': 'logged/_sidebar-home.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'News'}]

        context['notable_events'] = get_notable_events()

        return render(request, 'logged/news.tmpl', context)
