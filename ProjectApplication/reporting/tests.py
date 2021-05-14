from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population
from reporting.models import FundingInstrumentYearMissingData


class ReportingTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-reporting'))
        self.assertEqual(response.status_code, 200)


class FundingInstrumentYearMissingDataModel(TestCase):
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
