from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Avg, Max, Min, Count, F, Sum

from project_core.models import Call, Project


def calculate_number_of_calls():
    result = {}

    result['calls_per_year'] = Call.objects.filter(submission_deadline__lte=timezone.now()). \
        values(year=F('finance_year')). \
        annotate(aggregated=Count('*')). \
        order_by('finance_year')

    return result


def allocated_budget_per_year():
    result = {}

    result['allocated_budget_per_year'] = Project.objects. \
        values(year=F('call__finance_year')). \
        annotate(aggregated=Sum('allocated_budget')). \
        order_by('call__finance_year')

    return result


def allocated_budget_per_call():
    result = {}

    result['allocated_budget_per_call'] = Project.objects. \
        values(year=F('call__long_name')). \
        annotate(aggregated=Sum('allocated_budget')). \
        order_by('call__finance_year')

    return result


class Reporting(TemplateView):
    template_name = 'reporting/reporting.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(calculate_number_of_calls())

        context.update(allocated_budget_per_year())

        context.update(allocated_budget_per_call())

        context.update({'active_section': 'reporting',
                        'active_subsection': 'reporting',
                        'sidebar_template': 'reporting/_sidebar-reporting.tmpl',
                        'breadcrumb': [{'name': 'Reporting'}]})

        return context
