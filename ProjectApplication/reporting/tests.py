import datetime

from django.test import TestCase
from django.urls import reverse

from grant_management.models import GrantAgreement, Invoice
from project_core.models import OrganisationName
from project_core.tests import database_population
from reporting.models import FundingInstrumentYearMissingData


class ReportingTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-reporting'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Big Expeditions')
        self.assertContains(response, '20&#x27;000.00')

    def test_financial_information(self):
        response = self._client_management.get(reverse('logged-reporting'))
        create_project_with_invoices()
        self.assertContains(response, 'Big Expeditions')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['allocated_budget_per_call']['data']), 1)


class FundingInstrumentYearMissingDataModelTest(TestCase):
    def setUp(self):
        self._funding_instrument = database_population.create_funding_instrument()

    def test_is_missing_data_false(self):
        self.assertFalse(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT)[0])

    def test_is_missing_data_true(self):
        funding_instrument_year_missing_data = FundingInstrumentYearMissingData()
        funding_instrument_year_missing_data.missing_data_type = FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT
        funding_instrument_year_missing_data.save()

        self.assertTrue(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT)[0])

    def test_is_missing_data_true_only_one_year(self):
        funding_instrument_year_missing_data = FundingInstrumentYearMissingData()
        funding_instrument_year_missing_data.missing_data_type = FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT
        funding_instrument_year_missing_data.finance_year = 2016
        funding_instrument_year_missing_data.save()

        self.assertFalse(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT, year=2017)[0])

        self.assertTrue(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT, year=2016)[0])

    def test_is_missing_data_exact(self):
        funding_instrument_year_missing_data = FundingInstrumentYearMissingData()
        funding_instrument_year_missing_data.missing_data_type = FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT
        funding_instrument_year_missing_data.finance_year = 2016
        funding_instrument_year_missing_data.funding_instrument = self._funding_instrument
        funding_instrument_year_missing_data.save()

        self.assertTrue(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT,
            funding_instrument=self._funding_instrument,
            year=2016)[0])

        self.assertFalse(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_PROPOSAL_APPLICANT,
            funding_instrument=self._funding_instrument,
            year=2017)[0])

        self.assertFalse(FundingInstrumentYearMissingData.is_missing_data(
            FundingInstrumentYearMissingData.MissingDataType.CAREER_STAGE_FUNDED_PROJECT_PI,
            funding_instrument=self._funding_instrument,
            year=2016)[0])


def create_project_with_invoices():
    project2 = database_population.create_project(key='SPI-2020-002', title='Second test')
    principal_investigator = database_population.create_person_position(first_name='James',
                                                                        surname='Alan',
                                                                        orcid=None)
    project2.principal_investigator = principal_investigator
    project2.allocated_budget = 15_000
    project2.save()

    # This one is not paid yet:
    Invoice.objects.create(project=project2,
                           sent_for_payment_date=datetime.date(2021, 4, 5),
                           amount=1_000)

    # This one it is paid:
    Invoice.objects.create(project=project2,
                           sent_for_payment_date=datetime.date(2021, 4, 5),
                           paid_date=datetime.date(2021, 4, 5),
                           amount=1_500)

    grant_agreement = GrantAgreement.objects.create(project=project2,
                                                    signed_date=datetime.datetime(2020, 1, 4))


class ProjectsBalanceCsvTest(TestCase):
    def setUp(self):
        self._client_management = database_population.create_management_logged_client()

    def test_get_one_project(self):
        database_population.create_project()

        response = self._client_management.get(reverse('logged-reporting-finance-projects_balance-csv'))
        self.assertEqual(response.status_code, 200)
        lines = response.content.decode('utf-8').split('\r\n')

        self.assertEqual(len(lines), 3)

        self.assertEqual(lines[0], '\ufeffKey\tSigned date\tOrganisation\tTitle\tStart Date\tEnd Date\tAllocated budget\tBalance due')
        self.assertEqual(lines[1], 'SPI-2020-001\tNo grant agreement attached\t\tThis is a test project\t2020-01-10\t2022-05-07\t20000,00\t20000,00')
        self.assertEqual(lines[2], '')

    def test_get_two_projects(self):
        project1 = database_population.create_project()
        organisation_name = OrganisationName.objects.create(name='Some organisation')

        project1.principal_investigator.organisation_names.add(organisation_name)

        project2 = create_project_with_invoices()

        response = self._client_management.get(reverse('logged-reporting-finance-projects_balance-csv'))
        self.assertEqual(response.status_code, 200)
        lines = response.content.decode('utf-8').split('\r\n')

        self.assertEqual(len(lines), 4)

        self.assertEqual(lines[0], '\ufeffKey\tSigned date\tOrganisation\tTitle\tStart Date\tEnd Date\tAllocated budget\tBalance due')
        self.assertEqual(lines[1],
                         'SPI-2020-001\tNo grant agreement attached\tSome organisation\tThis is a test project\t2020-01-10\t2022-05-07\t20000,00\t20000,00')
        self.assertEqual(lines[2], 'SPI-2020-002\t04/01/2020\t\tSecond test\t2020-01-10\t2022-05-07\t15000,00\t13500,00')
        self.assertEqual(lines[3], '')
