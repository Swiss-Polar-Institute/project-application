from django.db.models import Count, F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from project_core.models import Call, Project, Gender, CareerStage, Proposal
from project_core.templatetags.thousands_separator import thousands_separator
from reporting.models import FundingInstrumentYearMissingData

NOT_IN_DB_HEADER = 'Not in DB'
NOT_IN_DB_TOOLTIP = 'Probably data imported before the Projects Application existed'


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

    def calculate_gender_totals(self, generic_queryset):
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
                    NOT_IN_DB_HEADER: '?',
                    }

        return {'Female': female,
                'Male': male,
                'Other': other,
                'Prefer not to say': prefer_not_to_say,
                NOT_IN_DB_HEADER: not_in_db,
                }


class CareerStageCalculator():
    def __init__(self, career_stage_field):
        self._career_stage_field = career_stage_field
        self._career_stages = None

    def calculate_career_stage_stats(self, generic_queryset):
        if self._career_stages is None:
            self._career_stages = CareerStage.objects.all()

        result = {}
        for career_stage in self._career_stages:
            result[career_stage.name] = generic_queryset.filter(**{self._career_stage_field: career_stage}).count()

        result[NOT_IN_DB_HEADER] = generic_queryset.filter(**{f'{self._career_stage_field}__isnull': True}).count()

        return result

    @staticmethod
    def career_stages_sorted():
        return CareerStage.objects.order_by('list_order')

    @staticmethod
    def header_names():
        result = []

        for career_stage in CareerStageCalculator.career_stages_sorted():
            result.append(career_stage.name)

        result.append(NOT_IN_DB_HEADER)

        return result


def gender_proposal_applicants_per_call():
    proposals_genders = []
    gender_percentage_calculator = GenderPercentageCalculator('applicant__person__gender')

    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.proposal_set

        percentages = gender_percentage_calculator.calculate_gender_totals(generic_queryset)
        percentages['Grant Scheme'] = call.funding_instrument.long_name
        percentages['Year'] = call.finance_year
        proposals_genders.append(percentages)

    result = {}
    result['data'] = proposals_genders
    result['headers'] = ['Grant Scheme', 'Year', 'Female', 'Male', 'Other', 'Prefer not to say', NOT_IN_DB_HEADER]
    result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}
    return result


def gender_project_principal_investigator_per_call():
    proposals_genders = []
    gender_percentage_calculator = GenderPercentageCalculator('principal_investigator__person__gender')

    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        generic_queryset = call.project_set

        percentages = gender_percentage_calculator.calculate_gender_totals(generic_queryset)
        percentages['Grant Scheme'] = call.funding_instrument.long_name
        percentages['Year'] = call.finance_year
        proposals_genders.append(percentages)

    result = {}
    result['headers'] = ['Grant Scheme', 'Year', 'Female', 'Male', 'Other', 'Prefer not to say', NOT_IN_DB_HEADER]
    result['data'] = proposals_genders
    result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}
    return result


def value_or_missing_data(is_missing_data, missing_data_reason, value):
    if is_missing_data:
        return missing_data_reason

    return value


def career_stage_proposal_applicants_per_year():
    result = {}

    career_stages = CareerStageCalculator.career_stages_sorted()

    data = []
    for year in Call.objects.all().values_list('finance_year', flat=True).distinct().order_by('finance_year'):
        row = {}
        row['Year'] = year
        is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT, year=year)

        for career_stage in career_stages:
            row[career_stage.name] = value_or_missing_data(is_missing_data,
                                                           missing_data_reason,
                                                           Proposal.objects.
                                                           filter(call__finance_year=year).
                                                           filter(applicant__career_stage=career_stage).
                                                           count())

        row[NOT_IN_DB_HEADER] = value_or_missing_data(is_missing_data,
                                                      missing_data_reason,
                                                      Project.objects.
                                                      filter(call__finance_year=year).
                                                      filter(principal_investigator__career_stage__isnull=True).
                                                      count()
                                                      )

        data.append(row)

    result['headers'] = ['Year'] + CareerStageCalculator.header_names()
    result['data'] = data
    result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

    return result


def career_stage_projects_principal_investigators_per_year():
    result = {}

    career_stages = CareerStageCalculator.career_stages_sorted()

    data = []
    for year in Call.objects.all().values_list('finance_year', flat=True).distinct().order_by('finance_year'):
        row = {}
        row['Year'] = year
        is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_FUNDED_PROJECT_PI, year=year)

        for career_stage in career_stages:
            row[career_stage.name] = value_or_missing_data(is_missing_data, missing_data_reason, Project.objects.
                                                           filter(call__finance_year=year).
                                                           filter(principal_investigator__career_stage=career_stage).
                                                           count())

        row[NOT_IN_DB_HEADER] = value_or_missing_data(is_missing_data, missing_data_reason, Project.objects.
                                                      filter(call__finance_year=year).
                                                      filter(principal_investigator__career_stage__isnull=True).
                                                      count()
                                                      )

        data.append(row)

    result['headers'] = result['headers'] = ['Year'] + CareerStageCalculator.header_names()
    result['data'] = data
    result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

    return result


def career_stage_proposal_applicants_per_call():
    career_stage_percentage_calculator = CareerStageCalculator('applicant__career_stage')

    data = []
    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT,
            funding_instrument=call.funding_instrument, year=call.finance_year)

        generic_queryset = call.proposal_set

        stats = career_stage_percentage_calculator.calculate_career_stage_stats(generic_queryset)

        for stat_key in stats.keys():
            if is_missing_data:
                stats[stat_key] = missing_data_reason

        stats['Grant Scheme'] = call.funding_instrument.long_name
        stats['Year'] = call.finance_year
        data.append(stats)

    result = {}
    result['headers'] = ['Grant Scheme', 'Year'] + career_stage_percentage_calculator.header_names()
    result['data'] = data
    result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

    return result


def career_stage_project_principal_investigator_per_call():
    career_stage_calculator = CareerStageCalculator('principal_investigator__career_stage')

    data = []
    for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
            order_by('long_name'):
        is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_FUNDED_PROJECT_PI,
            funding_instrument=call.funding_instrument, year=call.finance_year)

        generic_queryset = call.project_set

        stats = career_stage_calculator.calculate_career_stage_stats(generic_queryset)
        for stat in stats.keys():
            if is_missing_data:
                stats[stat] = missing_data_reason

        stats['Grant Scheme'] = call.funding_instrument.long_name
        stats['Year'] = call.finance_year
        data.append(stats)

    result = {}
    result['headers'] = ['Grant Scheme', 'Year'] + career_stage_calculator.header_names()
    result['data'] = data
    result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

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
