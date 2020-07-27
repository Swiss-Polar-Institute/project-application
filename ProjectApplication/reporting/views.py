from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Avg, Max, Min, Count

from project_core.models import Call


def calculate_number_of_calls():
    result = {}
    minimum_year = Call.objects.filter(submission_deadline__lte=timezone.now()).aggregate(Min('finance_year'))[
        'finance_year__min']
    maximum_year = Call.objects.filter(submission_deadline__lte=timezone.now()).aggregate(Max('finance_year'))[
        'finance_year__max']

    result['minimum_year'] = minimum_year
    result['maximum_year'] = maximum_year

    result['calls_per_year'] = Call.objects.filter(submission_deadline__lte=timezone.now()).values(
        'finance_year').annotate(number_of_calls=Count('id')).order_by('finance_year')

    return result


class Reporting(TemplateView):
    template_name = 'reporting/reporting.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(calculate_number_of_calls())

        context.update({'active_section': 'reporting',
                        'active_subsection': 'reporting',
                        'sidebar_template': 'reporting/_sidebar-reporting.tmpl',
                        'breadcrumb': [{'name': 'Reporting'}]})

        return context
