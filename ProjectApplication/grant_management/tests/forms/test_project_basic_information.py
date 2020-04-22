from datetime import date

from django.test import TestCase

from grant_management.forms.project_basic_information import ProjectBasicInformationForm
from project_core.tests import database_population


class ProjectBasicInformationFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_valid_change_basic_information(self):
        data = {'start_date': date(2021, 2, 5),
                'end_date': date(2021, 2, 15)
                }

        financial_report_item_form = ProjectBasicInformationForm(data=data, instance=self._project)
        self.assertTrue(financial_report_item_form.is_valid())
        financial_report_item_form.save()

        self._project.refresh_from_db()

        self.assertEqual(self._project.start_date, date(2021, 2, 5))
        self.assertEqual(self._project.end_date, date(2021, 2, 15))

    def test_invalid_change_basic_information(self):
        data = {'start_date': date(2021, 2, 25),
                'end_date': date(2021, 2, 15)
                }

        financial_report_item_form = ProjectBasicInformationForm(data=data, instance=self._project)
        self.assertFalse(financial_report_item_form.is_valid())
