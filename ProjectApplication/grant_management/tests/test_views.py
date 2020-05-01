from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from grant_management.models import Invoice, FinancialReport
from project_core.tests import database_population


class ProjectListTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-grant_management-project-list'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self._project.title)


class ProjectDetailsTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-project-detail', kwargs={'pk': self._project.id}))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self._project.title)


class FinancesViewUpdateTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-finances-update', kwargs={'project': self._project.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_valid_invoice(self):
        project_id = self._project.id
        data = MultiValueDict(
            {'invoices_form-TOTAL_FORMS': ['1'], 'invoices_form-INITIAL_FORMS': ['0'],
             'invoices_form-MIN_NUM_FORMS': ['1'], 'invoices_form-MAX_NUM_FORMS': ['1000'],
             'invoices_form-0-project': [str(project_id)], 'invoices_form-0-id': [''], 'invoices_form-0-DELETE': [''],
             'invoices_form-0-can_be_deleted': ['0'], 'invoices_form-0-due_date': ['22-01-2021'],
             'financial_reports_form-TOTAL_FORMS': ['1'], 'financial_reports_form-INITIAL_FORMS': ['1'],
             'financial_reports_form-MIN_NUM_FORMS': ['1'], 'financial_reports_form-MAX_NUM_FORMS': ['1000'],
             'financial_reports_form-0-project': [str(project_id)], 'financial_reports_form-0-id': [''],
             'financial_reports_form-0-DELETE': [''], 'financial_reports_form-0-can_be_deleted': ['0'],
             'financial_reports_form-0-file': [''], 'save_finances': ['Save Finances']
             })

        self.assertEqual(Invoice.objects.all().count(), 0)
        self.assertEqual(FinancialReport.objects.all().count(), 0)

        response = self._client_management.post(
            reverse('logged-grant_management-finances-update', kwargs={'project': self._project.id}),
            data=data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Invoice.objects.all().count(), 1)


class ProjectBasicInformationUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-project-update', kwargs={'pk': self._project.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        project_id = self._project.id

        self.assertEqual(self._project.start_date, date(2020, 1, 10))
        self.assertEqual(self._project.end_date, date(2022, 5, 7))

        data = MultiValueDict(
            {'start_date': ['10-05-2020'],
             'end_date': ['22-10-2020'],
             'save': ['Save Information']
             })

        response = self._client_management.post(
            reverse('logged-grant_management-project-update', kwargs={'pk': project_id}),
            data=data
        )

        self.assertEqual(response.status_code, 302)
        self._project.refresh_from_db()

        self.assertEqual(self._project.start_date, date(2020, 5, 10))
        self.assertEqual(self._project.end_date, date(2020, 10, 22))