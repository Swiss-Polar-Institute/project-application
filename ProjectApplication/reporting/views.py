import codecs
import csv
from _csv import QUOTE_NONNUMERIC

from django.db.models import Count, F, Sum, Min, Max
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from project_core.models import Call, Project, Gender, CareerStage, Proposal, FundingInstrument
from project_core.templatetags.thousands_separator import thousands_separator
from reporting.models import FundingInstrumentYearMissingData

NOT_IN_DB_HEADER = 'Not in DB'
NOT_IN_DB_TOOLTIP = 'Probably data imported before the Projects Application existed'


class CareerStagePerCallCalculator:
    def __init__(self, career_stage_field: str, foreign_key, missing_data):
        self._career_stage_field = career_stage_field
        self._foreign_key = foreign_key
        self._missing_data = missing_data

        self._career_stages = None

    def calculate_career_stage_stats(self, generic_queryset):
        if self._career_stages is None:
            self._career_stages = CareerStagePerYearCalculator._career_stages_sorted()

        result = {}
        for career_stage in self._career_stages:
            result[career_stage.name] = generic_queryset.filter(**{self._career_stage_field: career_stage}).count()

        result[NOT_IN_DB_HEADER] = generic_queryset.filter(**{f'{self._career_stage_field}__isnull': True}).count()

        return result

    def calculate_result(self):
        data = []
        for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
                order_by('long_name'):
            is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
                self._missing_data,
                funding_instrument=call.funding_instrument,
                year=call.finance_year)

            generic_queryset = getattr(call, self._foreign_key)

            stats = self.calculate_career_stage_stats(generic_queryset)

            for stat_key in stats.keys():
                if is_missing_data:
                    stats[stat_key] = missing_data_reason

            stats['Grant Scheme'] = call.funding_instrument.long_name
            stats['Year'] = call.finance_year
            data.append(stats)

        result = {}
        result['headers'] = ['Grant Scheme', 'Year'] + CareerStagePerYearCalculator._header_names()
        result['data'] = data
        result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

        return result


class CareerStagePerYearCalculator:
    def __init__(self, model, career_stage_field, missing_data_type):
        self._model = model
        self._career_stage_field = career_stage_field
        self._missing_data_type = missing_data_type

    def calculate_career_stage_stats(self, generic_queryset):
        if self._career_stages is None:
            self._career_stages = CareerStage.objects.all()

        result = {}
        for career_stage in self._career_stages:
            result[career_stage.name] = generic_queryset.filter(**{self._career_stage_field: career_stage}).count()

        result[NOT_IN_DB_HEADER] = generic_queryset.filter(**{f'{self._career_stage_field}__isnull': True}).count()

        return result

    @staticmethod
    def _career_stages_sorted():
        return CareerStage.objects.order_by('list_order')

    @staticmethod
    def _header_names():
        result = []

        for career_stage in CareerStagePerYearCalculator._career_stages_sorted():
            result.append(career_stage.name)

        result.append(NOT_IN_DB_HEADER)

        return result

    def calculate_result(self):
        data = []
        for year in Call.objects.all().values_list('finance_year', flat=True).distinct().order_by('finance_year'):
            row = {}
            row['Year'] = year
            is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
                self._missing_data_type, year=year)

            for career_stage in CareerStagePerYearCalculator._career_stages_sorted():
                row[career_stage.name] = value_or_missing_data(is_missing_data,
                                                               missing_data_reason,
                                                               self._model.objects.
                                                               filter(call__finance_year=year).
                                                               filter(**{self._career_stage_field: career_stage}).
                                                               count())

            row[NOT_IN_DB_HEADER] = value_or_missing_data(is_missing_data,
                                                          missing_data_reason,
                                                          self._model.objects.
                                                          filter(call__finance_year=year).
                                                          filter(**{f'{self._career_stage_field}__isnull': True}).
                                                          count())

            data.append(row)

        result = {}
        result['headers'] = ['Year'] + CareerStagePerYearCalculator._header_names()
        result['data'] = data
        result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

        return result


class GenderCalculator:
    def __init__(self, gender_field, foreign_key_field: str, missing_data_type):
        self._gender_field = gender_field
        self._foreign_key_field = foreign_key_field
        self._missing_data_type = missing_data_type

        self._grant_scheme_text = 'Grant Scheme'
        self._year_text = 'Year'

        self._gender_list = list(Gender.objects.all().order_by('name'))

        self._gender_name_list = []

        for gender in self._gender_list:
            self._gender_name_list.append(gender.name)

    def _calculate_genders(self, generic_queryset):
        result = {}
        for gender in self._gender_list:
            result[gender.name] = generic_queryset.filter(**{self._gender_field: gender.id}).count()

        result[NOT_IN_DB_HEADER] = generic_queryset.filter(**{f'{self._gender_field}__isnull': True}).count()

        return result

    def calculate_final_table(self):
        proposals_genders = []
        for call in Call.objects.filter(submission_deadline__lte=timezone.now()). \
                order_by('long_name'):
            generic_queryset = getattr(call, self._foreign_key_field)

            percentages = self._calculate_genders(generic_queryset)

            missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
                self._missing_data_type, funding_instrument=call.funding_instrument, year=call.finance_year)

            if missing_data:
                for data in percentages.keys():
                    percentages[data] = missing_data_reason

            percentages[self._grant_scheme_text] = call.funding_instrument.long_name
            percentages[self._year_text] = call.finance_year
            proposals_genders.append(percentages)

        result = {}
        result['headers'] = [self._grant_scheme_text, self._year_text] + self._gender_name_list + [NOT_IN_DB_HEADER]
        result['data'] = proposals_genders
        result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}
        return result


class ObjectsPerFundingInstrumentPerYear:
    def __init__(self, model, missing_data):
        self._model = model
        self._missing_data = missing_data

        self._funding_instruments = list(FundingInstrument.objects.all().order_by('long_name'))

        self._funding_instruments_long_names = []
        for funding_instrument in self._funding_instruments:
            self._funding_instruments_long_names.append(funding_instrument.long_name)

        self._start_year = Call.objects.aggregate(Min('finance_year'))['finance_year__min']
        self._end_year = Call.objects.aggregate(Max('finance_year'))['finance_year__max']

    def _get_headers(self):
        return ['Year'] + self._funding_instruments_long_names

    def calculate_result(self):
        data = []
        for year in range(self._start_year, self._end_year + 1):
            row = {}
            row['Year'] = year

            for funding_instrument in self._funding_instruments:
                is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
                    self._missing_data,
                    funding_instrument=funding_instrument,
                    year=year)
                if is_missing_data:
                    row[funding_instrument.long_name] = missing_data_reason
                    continue

                calls = Call.objects.filter(funding_instrument=funding_instrument).filter(finance_year=year)

                if calls.exists():
                    proposal_count = self._model.objects.filter(call__in=calls).count()
                    row[funding_instrument.long_name] = proposal_count
                else:
                    row[funding_instrument.long_name] = '-'

            data.append(row)

        result = {}
        result['headers'] = self._get_headers()
        result['data'] = data
        return result


def value_or_missing_data(is_missing_data, missing_data_reason, value):
    if is_missing_data:
        return missing_data_reason

    return value


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
        values(call_name=F('call__funding_instrument__long_name'),
               account_number=F('call__funding_instrument__short_name__account_number'),
               finance_year=F('call__finance_year')). \
        annotate(financial_support=Sum('allocated_budget')). \
        order_by('call__finance_year')

    data = []
    for row in allocated_budget_per_call:
        data.append({'Grant Scheme': row['call_name'],
                     'Account Number': row['account_number'],
                     'Year': row['finance_year'],
                     'Financial Support (CHF)': thousands_separator(row['financial_support'])
                     })

    result['headers'] = ['Grant Scheme', 'Account Number', 'Year', 'Financial Support (CHF)']
    result['data'] = data

    return result


def gender_proposal_applicants_per_call():
    gender_percentage_calculator = GenderCalculator('applicant__person__gender',
                                                    'proposal_set',
                                                    FundingInstrumentYearMissingData.MissingDataType.GENDER_PROPOSAL_APPLICANT)

    return gender_percentage_calculator.calculate_final_table()


def gender_project_principal_investigator_per_call():
    gender_percentage_calculator = GenderCalculator('principal_investigator__person__gender', 'project_set',
                                                    FundingInstrumentYearMissingData.MissingDataType.GENDER_FUNDED_PROJECT_PI)

    return gender_percentage_calculator.calculate_final_table()


def career_stage_proposal_applicants_per_year():
    career_stage_calculator = CareerStagePerYearCalculator(Proposal, 'applicant__career_stage',
                                                           FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT)

    return career_stage_calculator.calculate_result()


def career_stage_projects_principal_investigators_per_year():
    career_stage_calculator = CareerStagePerYearCalculator(Project, 'principal_investigator__career_stage',
                                                           FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_FUNDED_PROJECT_PI)

    return career_stage_calculator.calculate_result()


def career_stage_proposal_applicants_per_call():
    career_stage_calculator = CareerStagePerCallCalculator('applicant__career_stage', 'proposal_set',
                                                           FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT)

    return career_stage_calculator.calculate_result()


def career_stage_project_principal_investigator_per_call():
    career_stage_calculator = CareerStagePerCallCalculator('principal_investigator__career_stage', 'project_set',
                                                           FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_FUNDED_PROJECT_PI)

    return career_stage_calculator.calculate_result()


def proposals_per_funding_instrument():
    proposals_calculator = ObjectsPerFundingInstrumentPerYear(Proposal,
                                                              FundingInstrumentYearMissingData.MissingDataType.PROPOSALS)

    return proposals_calculator.calculate_result()


def projects_per_funding_instrument():
    projects_calculator = ObjectsPerFundingInstrumentPerYear(Project, None)

    return projects_calculator.calculate_result()


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

        context['proposals_per_funding_instrument'] = proposals_per_funding_instrument()

        context['projects_per_funding_instrument'] = projects_per_funding_instrument()

        context.update({'active_section': 'reporting',
                        'active_subsection': 'reporting',
                        'sidebar_template': 'reporting/_sidebar-reporting.tmpl',
                        'breadcrumb': [{'name': 'Reporting'}]})

        if 'tab' in self.request.GET:
            context['active_tab'] = self.request.GET['tab']
        else:
            context['active_tab'] = 'overview'

        return context


class ProjectsBalanceCsv(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        now = timezone.localtime()
        filename = (f'projects-balance-{now:%Y%m%d-%H%M}.csv')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        response.write(codecs.BOM_UTF8)

        headers = ['Key', 'Signed date', 'Organisation', 'Title', 'Allocated budget', 'Commitment balance']

        writer = csv.DictWriter(response, fieldnames=headers, quoting=QUOTE_NONNUMERIC)

        for project in Project.objects.all().order_by('key'):
            pi_organisations = project.principal_investigator.organisations_ordered_by_name_str()

            if hasattr(project, 'grantagreement'):
                if project.grantagreement.signed_date:
                    grant_agreement_signed_date = project.grantagreement.signed_date.strftime('%d/%m/%Y')
                else:
                    grant_agreement_signed_date = 'Grant agreement not signed'
            else:
                grant_agreement_signed_date = 'No grant agreement attached'

            row = {'Key': project.key,
                   'Signed date': grant_agreement_signed_date,
                   'Organisation': pi_organisations,
                   'Title': project.title,
                   'Allocated budget': project.allocated_budget,
                   'Commitment balance': 'TODO'
                   }

            writer.writerow(row)

        return response
