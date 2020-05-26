from datetime import datetime

from django.test import TestCase

from grant_management.forms.reports import FinancialReportItemModelForm
from grant_management.models import FinancialReport
from project_core.tests import database_population


class FinancialReportItemFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_valid_financial_report(self):
        data = {'project': self._project,
                'due_date': datetime(2020, 1, 12)
                }

        self.assertEqual(FinancialReport.objects.all().count(), 0)
        financial_report_item_form = FinancialReportItemModelForm(data=data)

        self.assertTrue(financial_report_item_form.is_valid())

        financial_report_item_form.save()

        self.assertEqual(FinancialReport.objects.all().count(), 1)

    def test_received_date_after_sent_date(self):
        data = {'project': self._project,
                'received_date': datetime(2020, 5, 5),
                'sent_for_approval_date': datetime(2020, 1, 5),
                'due_date': datetime(2020, 1, 5)
                }

        financial_report_item_form = FinancialReportItemModelForm(data=data)

        self.assertFalse(financial_report_item_form.is_valid())
        self.assertIn('sent_for_approval_date', financial_report_item_form.errors)

