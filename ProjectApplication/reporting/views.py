from django.utils import timezone
from django.db.models import Count, F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from project_core.models import Call, Project, Gender, CareerStage, Proposal
from project_core.templatetags.thousands_separator import thousands_separator


def calculate_number_of_calls():
    result = {}

    calls_per_year = Call.objects.filter(submission_deadline__lte=timezone.now()). \
        values(Year=F('finance_year')). \
        annotate(Calls=Count('*')). \
        order_by('finance_year')

    result['data'] = calls_per_year
    result['headers'] = ['Year', 'Calls']

    return result


def allocated_budget_per_year():
    result = {}

    financial_support_per_year = Project.objects. \
        values(year=F('call__finance_year')). \
        annotate(financial_support=Sum('allocated_budget')). \
        order_by('call__finance_year')

    data = []

    for row in financial_support_per_year:
        data.append({'Year': row['year'],
                     'Financial Support (CHF)': thousands_separator(row['financial_support'])
                     })

    result['data'] = data
    result['headers'] = ['Year', 'Financial Support (CHF)']
    return result


def allocated_budget_per_call():
    result = {}

    allocated_budget_per_call = Project.objects. \
        values(call_name=F('call__funding_instrument__long_name'), finance_year=F('call__finance_year')). \
        annotate(financial_support=Sum('allocated_budget')). \
        order_by('call__finance_year')

    data = []
    for row in allocated_budget_per_call:
        data.append({'Grant Scheme': row['call_name'],
                     'Year': row['finance_year'],
                     'Financial Support (CHF)': thousands_separator(row['financial_support'])
                     })

    result['headers'] = ['Grant Scheme', 'Year', 'Financial Support (CHF)']
    result['data'] = data

    return result


def percentage(number, total):
    if total == 0:
        return 'N/A'

    return f'{(number / total) * 100:.2f}%'


class GenderPercentageCalculator:
    def __init__(self, gender_field):
        self._gender_field = gender_field

        self._genders = None

    def _get_genders(self):
        genders = {}

        genders['female'] = Gender.objects.get(name='Female')
        genders['male'] = Gender.objects.get(name='Male')
        genders['other'] = Gender.objects.get(name='Other')
        genders['prefer_not_to_say'] = Gender.objects.get(name='Prefer not to say')

        return genders

    def calculate_gender_percentages(self, generic_queryset):
        if self._genders is None:
            self._genders = self._get_genders()

        total = generic_queryset.count()

        female = generic_queryset.filter(**{self._gender_field: self._genders['female']}).count()
        male = generic_queryset.filter(**{self._gender_field: self._genders['male']}).count()
        other = generic_queryset.filter(**{self._gender_field: self._genders['other']}).count()
        prefer_not_to_say = generic_queryset.filter(**{self._gender_field: self._genders['prefer_not_to_say']}).count()
        not_in_db = generic_queryset.filter(**{f'{self._gender_field}__isnull': True}).count()

        if total != female + male + other + prefer_not_to_say + not_in_db:
            # The total should be the same as adding the other categories. It wouldn't be the same
            # if a category is added but this function is not updated. If this function is updated
            # the template needs to be updated as well (it's not dynamic at the moment)
            return {'Female': '?',
                    'Male': '?',
                    'Other': '?',
                    'Prefer not to say': '?',
                    'Not in DB': '?',
                    }

        female_percentage = percentage(female, total)
        male_percentage = percentage(male, total)
        other_percentage = percentage(other, total)
        prefer_not_to_say_percentage = percentage(prefer_not_to_say, total)
        not_in_db_percentage = percentage(not_in_db, total)

        return {'Female': female_percentage,
                'Male': male_percentage,
                'Other': other_percentage,
                'Prefer not to say': prefer_not_to_say_percentage,
                'Not in DB': not_in_db_percentage,
                'Total': total
                }


class CareerStagePercentageCalculator():
    def __init__(self, career_stage_field):
        self._career_stage_field = career_stage_field
        self._career_stages = None

    def calculate_career_stage_percentages(self, generic_queryset):
        if self._career_stages is None:
            self._career_stages = CareerStage.objects.all()

        result = {}
        for career_stage in self._career_stages:
            result[career_stage.name] = generic_queryset.filter(**{self._career_stage_field: career_stage}).count()
            result['Unknown'] = generic_queryset.filter(**{f'{self._career_stage_field}__isnull': True}).count()

        return result

    @staticmethod
    def header_names():
        return ["Undergraduate / master's student", 'PhD student', 'Post-doc < 3 years since PhD award date',
                'Established scientist', 'Other',
                'Unknown']


def gender_proposal_applicants_per_call():
    proposals_genders = []
    gender_percentage_calculator = GenderPercentageCalculator('applicant__person__gender')

    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.proposal_set

        percentages = gender_percentage_calculator.calculate_gender_percentages(generic_queryset)
        percentages['Grant Scheme'] = call.funding_instrument.long_name
        percentages['Year'] = call.finance_year
        proposals_genders.append(percentages)

    result = {}
    result['data'] = proposals_genders
    result['headers'] = ['Grant Scheme', 'Year', 'Female', 'Male', 'Other', 'Prefer not to say', 'Not in DB', 'Total']
    return result


def gender_project_principal_investigator_per_call():
    proposals_genders = []
    gender_percentage_calculator = GenderPercentageCalculator('principal_investigator__person__gender')

    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.project_set

        percentages = gender_percentage_calculator.calculate_gender_percentages(generic_queryset)
        percentages['Grant Scheme'] = call.funding_instrument.long_name
        percentages['Year'] = call.finance_year
        proposals_genders.append(percentages)

    result = {}
    result['headers'] = ['Grant Scheme', 'Year', 'Female', 'Male', 'Other', 'Prefer not to say', 'Not in DB', 'Total']
    result['data'] = proposals_genders
    return result


def career_stage_proposal_applicants_per_year():
    result = {}

    career_stages = CareerStage.objects.all().order_by('name')

    data = []
    for year in Call.objects.all().values_list('finance_year', flat=True).distinct().order_by('finance_year'):
        row = {}
        row['Year'] = year
        for career_stage in career_stages:
            row[career_stage.name] = Proposal.objects. \
                filter(call__finance_year=year). \
                filter(applicant__career_stage=career_stage). \
                count()

            row['Unknown'] = Project.objects. \
                filter(call__finance_year=year). \
                filter(principal_investigator__career_stage__isnull=True). \
                count()

        data.append(row)

    result['headers'] = ['Year'] + CareerStagePercentageCalculator.header_names()
    result['data'] = data

    return result


def career_stage_projects_principal_investigators_per_year():
    result = {}

    career_stages = CareerStage.objects.all().order_by('name')

    data = []
    for year in Call.objects.all().values_list('finance_year', flat=True).distinct().order_by('finance_year'):
        row = {}
        row['Year'] = year
        for career_stage in career_stages:
            row[career_stage.name] = Project.objects. \
                filter(call__finance_year=year). \
                filter(principal_investigator__career_stage=career_stage). \
                count()

        row['Unknown'] = Project.objects. \
            filter(call__finance_year=year). \
            filter(principal_investigator__career_stage__isnull=True). \
            count()

        data.append(row)

    result['headers'] = result['headers'] = ['Year'] + CareerStagePercentageCalculator.header_names()
    result['data'] = data

    return result


def career_stage_proposal_applicants_per_call():
    career_stage_percentage_calculator = CareerStagePercentageCalculator('applicant__career_stage')

    data = []
    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.proposal_set

        percentages = career_stage_percentage_calculator.calculate_career_stage_percentages(generic_queryset)
        percentages['Grant Scheme'] = call.funding_instrument.long_name
        percentages['Year'] = call.finance_year
        data.append(percentages)

    result = {}
    result['headers'] = ['Grant Scheme', 'Year'] + career_stage_percentage_calculator.header_names()
    result['data'] = data
    return result


def career_stage_project_principal_investigator_per_call():
    career_stage_percentage_calculator = CareerStagePercentageCalculator('principal_investigator__career_stage')

    data = []
    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.project_set

        percentages = career_stage_percentage_calculator.calculate_career_stage_percentages(generic_queryset)
        percentages['Grant Scheme'] = call.funding_instrument.long_name
        percentages['Year'] = call.finance_year
        data.append(percentages)

    result = {}
    result['headers'] = ['Grant Scheme', 'Year'] + career_stage_percentage_calculator.header_names()
    result['data'] = data
    return result


class Reporting(TemplateView):
    template_name = 'reporting/reporting.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls_per_year'] = calculate_number_of_calls()

        context['allocated_budget_per_year'] = allocated_budget_per_year()

        context['allocated_budget_per_call'] = allocated_budget_per_call()

        context['proposals_genders'] = gender_proposal_applicants_per_call()

        context['projects_genders'] = gender_project_principal_investigator_per_call()

        context['career_stage_proposal_applicants_per_year'] = career_stage_proposal_applicants_per_year()

        context[
            'career_stage_projects_principal_investigators_per_year'] = career_stage_projects_principal_investigators_per_year()

        context['career_stage_proposal_applicants_per_call'] = career_stage_proposal_applicants_per_call()

        context[
            'career_stage_project_principal_investigator_per_call'] = career_stage_project_principal_investigator_per_call()

        context.update({'active_section': 'reporting',
                        'active_subsection': 'reporting',
                        'sidebar_template': 'reporting/_sidebar-reporting.tmpl',
                        'breadcrumb': [{'name': 'Reporting'}]})

        if 'tab' in self.request.GET:
            context['active_tab'] = self.request.GET['tab']
        else:
            context['active_tab'] = 'finance'

        return context
