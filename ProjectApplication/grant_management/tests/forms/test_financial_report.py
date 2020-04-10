from datetime import datetime

from django.test import TestCase

from grant_management.forms.financial_reports import FinancialReportItemForm
from project_core.tests import database_population


class FinancialReportItemFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_valid_financial_report(self):
        data = {'project': self._project,
                'due_date': datetime(2020, 1, 5)
                }

        financial_report_item_form = FinancialReportItemForm(data=data)

        self.assertTrue(financial_report_item_form.is_valid())

    def test_reception_date_after_sent_date(self):
        data = {'project': self._project,
                'reception_date': datetime(2020, 5, 5),
                'sent_date': datetime(2020, 1, 5)
                }

        financial_report_item_form = FinancialReportItemForm(data=data)

        self.assertFalse(financial_report_item_form.is_valid())