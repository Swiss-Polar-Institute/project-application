from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Avg, Max, Min, Count, F, Sum, Q

from project_core.models import Call, Project, Gender


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


def calculate_gender_percentages(generic_queryset, gender_field):
    female_gender = Gender.objects.get(name='Female')
    male_gender = Gender.objects.get(name='Male')
    other_gender = Gender.objects.get(name='Other')
    prefer_not_to_say_gender = Gender.objects.get(name='Prefer not to say')

    total = generic_queryset.count()

    female = generic_queryset.filter(**{gender_field: female_gender}).count()
    male = generic_queryset.filter(**{gender_field: male_gender}).count()
    other = generic_queryset.filter(**{gender_field: other_gender}).count()
    prefer_not_to_say = generic_queryset.filter(**{gender_field: prefer_not_to_say_gender}).count()
    not_in_db = generic_queryset.filter(**{f'{gender_field}__isnull': True}).count()

    if total != female + male + other + prefer_not_to_say + not_in_db:
        # The total should be the same as adding the other categories. It wouldn't be the same
        # if a category is added but this function is not updated. If this function is updated
        # the template needs to be updated as well (it's not dynamic at the moment)
        return {'female_percentage': '?',
                'male_percentage': '?',
                'other_percentage': '?',
                'prefer_not_to_say_percentage': '?',
                'not_in_db_percentage': '?',
                }

    if total == 0:
        female_percentage = male_percentage = other_percentage = \
            prefer_not_to_say_percentage = not_in_db_percentage = None
    else:
        female_percentage = (female / total) * 100
        male_percentage = (male / total) * 100
        other_percentage = (other / total) * 100
        prefer_not_to_say_percentage = (prefer_not_to_say / total) * 100
        not_in_db_percentage = (not_in_db / total) * 100

    print(female_percentage)

    return {'female_percentage': female_percentage,
            'male_percentage': male_percentage,
            'other_percentage': other_percentage,
            'prefer_not_to_say_percentage': prefer_not_to_say_percentage,
            'not_in_db_percentage': not_in_db_percentage,
            }


def gender_proposal_applicants_per_call():
    proposals_genders = []
    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.proposal_set

        percentages = calculate_gender_percentages(generic_queryset, 'applicant__person__gender')
        percentages['call_name'] = call.long_name
        proposals_genders.append(percentages)

    result = {}
    result['proposals_genders'] = proposals_genders
    return result


class Reporting(TemplateView):
    template_name = 'reporting/reporting.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(calculate_number_of_calls())

        context.update(allocated_budget_per_year())

        context.update(allocated_budget_per_call())

        context.update(gender_proposal_applicants_per_call())

        context.update({'active_section': 'reporting',
                        'active_subsection': 'reporting',
                        'sidebar_template': 'reporting/_sidebar-reporting.tmpl',
                        'breadcrumb': [{'name': 'Reporting'}]})

        return context
