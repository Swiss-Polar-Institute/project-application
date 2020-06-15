from django.test import TestCase
from django.urls import reverse

from grant_management.forms.close_project import CloseProjectModelForm
from grant_management.models import Invoice
from project_core.models import Project
from project_core.tests import database_population


class CloseProjectFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._user = database_population.create_management_user()

    def test_aborted(self):
        data = {'status': 'Aborted',
                'abortion_reason': 'Permit did not arrive on time',
                'close': 'Close',
                'ignore_allocated_budget_not_fully_paid': True
                }

        self.assertEqual(self._project.status, Project.ONGOING)

        close_project_form = CloseProjectModelForm(data=data, instance=self._project)

        self.assertTrue(close_project_form.is_valid())

        close_project_form.close(self._user)

        self.assertEqual(self._project.status, Project.ABORTED)

    def test_completed(self):
        data = {'status': 'Completed',
                'abortion_reason': '',
                'close': 'Close',
                'ignore_allocated_budget_not_fully_paid': True
                }

        self.assertEqual(self._project.status, Project.ONGOING)

        close_project_form = CloseProjectModelForm(data=data, instance=self._project)

        self.assertTrue(close_project_form.is_valid())

        close_project_form.close(self._user)

        self.assertEqual(self._project.status, Project.COMPLETED)

    def test_unpaid_invoice_cannot_close(self):
        data = {'status': 'Completed',
                'abortion_reason': '',
                'close': 'Close'
                }

        Invoice.objects.create(due_date=self._project.start_date,
                               project=self._project)

        self.assertEqual(self._project.status, Project.ONGOING)

        close_project_form = CloseProjectModelForm(data=data, instance=self._project)

        self.assertFalse(close_project_form.is_valid())

        self.assertEqual(close_project_form.errors['status'][0], 'Cannot be closed: there are unpaid invoices')

    def test_unpaid_invoice_no_close_button_displayed(self):
        Invoice.objects.create(due_date=self._project.start_date,
                               project=self._project)

        c = database_population.create_management_logged_client()

        response = c.get(reverse('logged-grant_management-close_project', kwargs={'project': self._project.id}))

        self.assertNotContains(response, 'name="close"')

    def test_close_button_displayed(self):
        c = database_population.create_management_logged_client()

        response = c.get(reverse('logged-grant_management-close_project', kwargs={'project': self._project.id}))

        self.assertContains(response, 'name="close"')
