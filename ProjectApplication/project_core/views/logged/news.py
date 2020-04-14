from datetime import datetime, timedelta

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from grant_management.models import Invoice
from project_core.models import Call
from project_core.templatetags.request_is_reviewer import request_is_reviewer


def create_notable_event(date, description):
    return {'date': date,
            'description': mark_safe(description)
            }


def get_notable_events():
    notable_events = []
    date_now = timezone.now()
    date_1_week_ago = date_now - timedelta(days=5)

    for call_open in Call.objects.filter(call_open_date__gte=date_1_week_ago):
        url = reverse('logged-call-detail', kwargs={'pk': call_open.id})

        notable_events.append(
            create_notable_event(call_open.call_open_date,
                                 f'Call open: <a href="{url}">{call_open.short_name}</a>'))

    for call_close in Call.objects.filter(submission_deadline__gte=date_1_week_ago):
        url = reverse('logged-call-detail', kwargs={'pk': call_close.id})

        notable_events.append(
            create_notable_event(call_close.submission_deadline,
                                 f'Call close: <a href="{url}">{call_close.short_name}</a>'))

    # for project_start in Project.objects.filter(start_date__gte=date_1_week_ago):
    #     notable_events.append(
    #         create_notable_event(project_start.start_date, f'Project <em>{project_start.title}</em> starts')
    #     )
    #
    # for project_end in Project.objects.filter(start_date__gte=date_1_week_ago):
    #     notable_events.append(
    #         create_notable_event(project_end.end_date, f'Project <em>{project_end.title}</em> ends')
    #     )

    # for invoice_due in Invoice.objects.filter(due_date__gte=date_1_week_ago):
    #     notable_events.append(
    #         create_notable_event(invoice_due.due_date, f'Invoice due')
    #     )

    notable_events.append(create_notable_event(datetime.today(), '<strong>TODAY</strong>'))

    return notable_events


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
