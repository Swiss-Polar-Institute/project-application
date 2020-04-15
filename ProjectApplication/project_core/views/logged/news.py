from datetime import datetime, timedelta

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from evaluation.models import CallEvaluation
from grant_management.models import Invoice
from project_core.models import Call, Project
from project_core.templatetags.request_is_reviewer import request_is_reviewer


def create_news(date, description):
    return {'date': date,
            'description': mark_safe(description)
            }


def create_news_project(date, description, project):
    news = create_news(date, description)

    project_url = reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})
    pi_name_url = reverse('logged-person-position-detail', kwargs={'pk': project.principal_investigator.id})

    news['project_title'] = mark_safe(f'<a href="{project_url}">{project.title}</a>')
    news['pi_name'] = mark_safe(f'<a href="{pi_name_url}">{project.principal_investigator.person}</a>')
    news['institution'] = project.principal_investigator.organisations_ordered_by_name_str()

    return news


def date_1_week_ago(date):
    return date - timedelta(days=5)


def get_project_news():
    today = datetime.today()
    starts = date_1_week_ago(today)

    news = []

    for invoice in Project.objects.filter(start_date__gte=starts):
        news.append(
            create_news_project(invoice.start_date, f'Starts',
                                invoice)
        )

    for project in Project.objects.filter(start_date__gte=starts):
        news.append(
            create_news_project(project.end_date, f'Ends', project)
        )

    for invoice in Invoice.objects.filter(due_date__gte=starts):
        news.append(
            create_news_project(invoice.due_date, f'Invoice due', invoice.project)
        )

    bold_today = mark_safe('<strong>TODAY</strong>')
    news.append({'date': today,
                 'project_title': bold_today,
                 'pi_name': bold_today,
                 'institution': bold_today,
                 'description': bold_today})

    return news


def get_call_news():
    today = datetime.today()
    starts = date_1_week_ago(today)

    news = []

    for call_open in Call.objects.filter(call_open_date__gte=starts):
        url = reverse('logged-call-detail', kwargs={'pk': call_open.id})

        news.append(
            create_news(call_open.call_open_date,
                        f'Call open: <a href="{url}">{call_open.short_name}</a>'))

    for call_close in Call.objects.filter(submission_deadline__gte=starts):
        url = reverse('logged-call-detail', kwargs={'pk': call_close.id})

        news.append(
            create_news(call_close.submission_deadline,
                        f'Call close: <a href="{url}">{call_close.short_name}</a>'))

    for call_evaluation in CallEvaluation.objects.filter(panel_date__gte=starts):
        url = reverse('logged-call-evaluation-detail', kwargs={'pk': call_evaluation.id})

        news.append(
            create_news(call_evaluation.panel_date,
                        f'Panel for call <a href="{url}">{call_evaluation.call.short_name}</a>')

        )

    news.append(create_news(today, '<strong>TODAY</strong>'))

    return news


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

        context['call_news'] = get_call_news()
        context['project_news'] = get_project_news()

        return render(request, 'logged/news.tmpl', context)
