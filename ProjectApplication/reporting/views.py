import datetime
import io
from decimal import Decimal

import xlsxwriter
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

            stats['Grant Scheme'] = call.long_name_without_finance_year()
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

        if self._model == Proposal:
            self._finance_year_filter_key = 'call__finance_year'
        elif self._model == Project:
            self._finance_year_filter_key = 'finance_year'
        else:
            assert False

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

    def _calculate_min_year(self) -> int:
        # Using the minimum to have '-' if needed for old calls
        # (see _calculate_max_year)
        return min(
            Call.objects.aggregate(Min('finance_year'))['finance_year__min'],
            Project.objects.aggregate(Min('finance_year'))['finance_year__min']
        )

    def _calculate_max_year(self) -> int:
        # Using the maximum because there might not be calls for a year but
        # there might be funded projects (created not from a call)
        return max(
            Call.objects.aggregate(Max('finance_year'))['finance_year__max'],
            Project.objects.aggregate(Max('finance_year'))['finance_year__max']
        )

    def calculate_result(self):
        data = []

        for funding_instrument in FundingInstrument.objects.all().order_by('long_name'):
            min_year = self._calculate_min_year()
            max_year = self._calculate_max_year()

        # for year in Call.objects.all().values_list('finance_year', flat=True).distinct().order_by('finance_year'):
        for year in range(self._calculate_min_year(), self._calculate_max_year() + 1):
            row = {}
            row['Year'] = year
            is_missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
                self._missing_data_type, year=year)

            for career_stage in CareerStagePerYearCalculator._career_stages_sorted():
                row[career_stage.name] = value_or_missing_data(is_missing_data,
                                                               missing_data_reason,
                                                               self._model.objects.
                                                               filter(**{self._finance_year_filter_key: year}).
                                                               filter(**{self._career_stage_field: career_stage}).
                                                               count())

            row[NOT_IN_DB_HEADER] = value_or_missing_data(is_missing_data,
                                                          missing_data_reason,
                                                          self._model.objects.
                                                          filter(**{self._finance_year_filter_key: year}).
                                                          filter(**{f'{self._career_stage_field}__isnull': True}).
                                                          count())

            data.append(row)

        result = {}
        result['headers'] = ['Year'] + CareerStagePerYearCalculator._header_names()
        result['data'] = data
        result['header_tooltips'] = {NOT_IN_DB_HEADER: NOT_IN_DB_TOOLTIP}

        return result


def not_none_or_function(item1, item2, function):
    if item1 is None and item2 is not None:
        return item2
    elif item1 is not None and item2 is None:
        return item1
    elif item1 is None and item2 is None:
        return None
    else:
        return function(item1, item2)


def calculate_min_year_for_funding_instrument(funding_instrument):
    projects_min_year = Project.objects.filter(funding_instrument=funding_instrument).aggregate(Min('finance_year'))[
        'finance_year__min']
    proposals_min_year = \
        Proposal.objects.filter(call__funding_instrument=funding_instrument).filter(call__callevaluation__isnull=False).aggregate(Min('call__finance_year'))[
            'call__finance_year__min']

    return not_none_or_function(projects_min_year, proposals_min_year, min)


def calculate_max_year_for_funding_instrument(funding_instrument):
    projects_max_year = Project.objects.filter(funding_instrument=funding_instrument).aggregate(Max('finance_year'))[
        'finance_year__max']
    proposals_max_year = \
        Proposal.objects.filter(call__funding_instrument=funding_instrument).filter(call__callevaluation__isnull=False).aggregate(Max('call__finance_year'))[
            'call__finance_year__max']

    return not_none_or_function(projects_max_year, proposals_max_year, max)


class GenderCalculator:
    def __init__(self, main_model, missing_data_type):
        self._main_model = main_model
        self._missing_data_type = missing_data_type

        self._grant_scheme_text = 'Grant Scheme'
        self._year_text = 'Year'

        self._gender_list = list(Gender.objects.all().order_by('name'))

        self._gender_name_list = []

        if self._main_model == Proposal:
            self._gender_field = 'applicant__person__gender'
        elif self._main_model == Project:
            self._gender_field = 'principal_investigator__person__gender'
        else:
            assert False

        for gender in self._gender_list:
            self._gender_name_list.append(gender.name)

    def _calculate_genders(self, generic_queryset):
        result = {}
        for gender in self._gender_list:
            result[gender.name] = generic_queryset.filter(**{self._gender_field: gender.id}).count()

        result[NOT_IN_DB_HEADER] = generic_queryset.filter(**{f'{self._gender_field}__isnull': True}).count()

        return result

    def _calculate_min_year_for_funding_instrument(self, funding_instrument):
        return Project.objects.filter(funding_instrument=funding_instrument).aggregate(Min('finance_year'))[
            'finance_year__min']

    def _calculate_max_year_for_funding_instrument(self, funding_instrument):
        return Project.objects.filter(funding_instrument=funding_instrument).aggregate(Max('finance_year'))[
            'finance_year__max']

    def calculate_result(self):
        data = []

        for funding_instrument in FundingInstrument.objects.all().order_by('long_name'):
            min_year = calculate_min_year_for_funding_instrument(funding_instrument)
            max_year = calculate_max_year_for_funding_instrument(funding_instrument)

            if min_year is None or max_year is None:
                continue

            for finance_year in range(min_year, max_year + 1):
                if self._main_model == Proposal:
                    generic_queryset = Proposal.objects. \
                        filter(call__finance_year=finance_year). \
                        filter(call__funding_instrument=funding_instrument). \
                        order_by('call__long_name')
                elif self._main_model == Project:
                    generic_queryset = Project.objects.filter(finance_year=finance_year). \
                        filter(funding_instrument=funding_instrument). \
                        order_by('funding_instrument__long_name')
                else:
                    assert False

                percentages = self._calculate_genders(generic_queryset)

                missing_data, missing_data_reason = FundingInstrumentYearMissingData.is_missing_data(
                    self._missing_data_type, funding_instrument=funding_instrument, year=finance_year)

                if missing_data:
                    for key in percentages.keys():
                        percentages[key] = missing_data_reason

                percentages[self._grant_scheme_text] = funding_instrument.long_name
                percentages[self._year_text] = finance_year
                data.append(percentages)

        result = {}
        result['headers'] = [self._grant_scheme_text, self._year_text] + self._gender_name_list + [NOT_IN_DB_HEADER]
        result['data'] = data
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

        self._start_year = Project.objects.aggregate(Min('finance_year'))['finance_year__min']
        self._end_year = Project.objects.aggregate(Max('finance_year'))['finance_year__max']

    def _get_headers(self):
        return ['Year'] + self._funding_instruments_long_names

    def _count_objects(self, funding_instrument, year):
        if self._model == Proposal:
            calls = Call.objects.filter(funding_instrument=funding_instrument).filter(finance_year=year)

            if calls.exists():
                return self._model.objects.filter(call__in=calls).count()
            else:
                return '-'
        elif self._model == Project:
            return self._model.objects.filter(funding_instrument=funding_instrument).filter(finance_year=year).count()
        else:
            assert False

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

                row[funding_instrument.long_name] = self._count_objects(funding_instrument, year)

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


def calculate_paid_so_far_year(year):
    total = 0

    for project in Project.objects.filter(finance_year=year):
        total += project.invoices_paid_amount()

    return total


def calculate_open_for_payment(year):
    total = 0

    for project in Project.objects.filter(finance_year=year):
        if project.is_active():
            total += project.allocated_budget - project.invoices_paid_amount()
        else:
            # If the project is closed
            pass

    return total


def allocated_budget_per_year():
    result = {}

    financial_support_per_year = Project.objects. \
        values(year=F('finance_year')). \
        annotate(commitment=Sum('allocated_budget')). \
        order_by('finance_year')

    data = []

    for row in financial_support_per_year:
        year = row['year']
        commitment = row['commitment']

        data.append({'Year': year,
                     'Commitment (CHF)': thousands_separator(commitment),
                     'Paid to date (CHF)': thousands_separator(calculate_paid_so_far_year(year)),
                     'Open for payment (CHF)': thousands_separator(calculate_open_for_payment(year)),
                     })

    result['data'] = data
    result['headers'] = ['Year', 'Commitment (CHF)', 'Paid to date (CHF)', 'Open for payment (CHF)']

    # result['header_tooltips'] = {'Open for payment (CHF)': ''}

    return result


def calculate_paid_so_far_funding_instrument_year(funding_instrument_long_name, year):
    total = 0

    for project in Project.objects.filter(funding_instrument__long_name=funding_instrument_long_name). \
            filter(finance_year=year):
        total += project.invoices_paid_amount()

    return total


def calculate_open_for_payment_funding_instrument_year(funding_instrument_long_name, year):
    total = 0

    for project in Project.objects.filter(funding_instrument__long_name=funding_instrument_long_name). \
            filter(finance_year=year):
        if project.is_active():
            total += project.allocated_budget - project.invoices_paid_amount()
        else:
            # If the project is closed
            pass

    return total


def allocated_budget_per_call():
    result = {}

    allocated_budget_per_call = Project.objects. \
        values(call_name=F('funding_instrument__long_name'),
               account_number=F('funding_instrument__short_name__account_number'),
               finance_year_=F('finance_year')). \
        annotate(financial_support=Sum('allocated_budget')). \
        order_by('finance_year')

    data = []
    for row in allocated_budget_per_call:
        funding_instrument_long_name = row['call_name']
        year = row['finance_year_']

        paid_so_far = calculate_paid_so_far_funding_instrument_year(funding_instrument_long_name, year)
        open_for_payment = calculate_open_for_payment_funding_instrument_year(funding_instrument_long_name, year)

        data.append({'Grant Scheme': row['call_name'],
                     'Account Number': row['account_number'],
                     'Year': row['finance_year_'],
                     'Commitment (CHF)': thousands_separator(row['financial_support']),
                     'Paid to date (CHF)': thousands_separator(paid_so_far),
                     'Open for payment (CHF)': thousands_separator(open_for_payment),
                     })

    result['headers'] = ['Grant Scheme', 'Account Number', 'Year', 'Commitment (CHF)', 'Paid to date (CHF)',
                         'Open for payment (CHF)']
    result['data'] = data

    return result


def gender_proposal_applicants_per_call():
    gender_percentage_calculator = GenderCalculator(Proposal,
                                                    FundingInstrumentYearMissingData.MissingDataType.GENDER_PROPOSAL_APPLICANT)

    return gender_percentage_calculator.calculate_result()


def gender_project_principal_investigator_per_call():
    gender_percentage_calculator = GenderCalculator(Project,
                                                    FundingInstrumentYearMissingData.MissingDataType.GENDER_FUNDED_PROJECT_PI)

    return gender_percentage_calculator.calculate_result()


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

        context['active_tab'] = self.request.GET.get('tab', 'overview')

        return context


def format_number_for_swiss_locale(number):
    return str(number).replace('.', ',')


def format_date_for_swiss_locale(date):
    return date.strftime('%d/%m/%Y')


class ProjectsBalanceExcel(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _headers():
        return ['Key', 'Signed date', 'Organisation', 'Title', 'Start date', 'End date', 'Allocated budget',
                'Balance due']

    @staticmethod
    def _rows():
        rows = []
        for project in Project.objects.all().order_by('key'):
            pi_organisations = project.principal_investigator.organisations_ordered_by_name_str()

            if hasattr(project, 'grantagreement'):
                if project.grantagreement.signed_date:
                    grant_agreement_signed_date = project.grantagreement.signed_date
                else:
                    grant_agreement_signed_date = 'Grant agreement not signed'
            else:
                grant_agreement_signed_date = 'No grant agreement attached'

            balance_due = project.allocated_budget - project.invoices_paid_amount()

            rows.append({'Key': project.key,
                         'Signed date': grant_agreement_signed_date,
                         'Organisation': pi_organisations,
                         'Title': project.title,
                         'Start date': project.start_date if project.start_date else 'N/A',
                         'End date': project.end_date if project.end_date else 'N/A',
                         'Allocated budget': project.allocated_budget,
                         'Balance due': balance_due,
                         })

        return rows

    def get(self, request, *args, **kwargs):
        now = timezone.localtime()
        filename = f'projects-balance-{now:%Y%m%d-%H%M}.xlsx'

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        col_widths = {
            'Key': 12,
            'Organisation': 18,
            'Title': 44,
            'Signed date': 12,
            'Start date': 12,
            'End date': 12,
            'Allocated budget': 12,
            'Balance due': 12
        }

        response.content = excel_dict_writer(filename,
                                             ProjectsBalanceExcel._headers(),
                                             ProjectsBalanceExcel._rows(),
                                             col_widths)

        return response


def excel_dict_writer(filename, headers, rows, col_widths):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    worksheet.write_row(0, 0, headers)

    date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})
    decimal_format = workbook.add_format({'num_format': "#,##0.00"})

    for row_index, row in enumerate(rows, 1):
        to_use_headers = headers.copy()

        for header_name, cell_value in row.items():
            column_index = headers.index(header_name)
            to_use_headers.remove(header_name)

            if isinstance(cell_value, datetime.date):
                worksheet.write_datetime(row_index, column_index, cell_value, date_format)
            elif isinstance(cell_value, Decimal):
                worksheet.write_number(row_index, column_index, cell_value, decimal_format)
            else:
                worksheet.write(row_index, column_index, cell_value)

        assert to_use_headers == []

    for col_width_name, col_width in col_widths.items():
        column_index = headers.index(col_width_name)

        worksheet.set_column(column_index, column_index, col_width)

    workbook.close()

    output.seek(0)

    return output
