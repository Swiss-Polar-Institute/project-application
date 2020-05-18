from datetime import datetime

from django.test import TestCase

from grant_management.forms.installments import InstallmentModelForm
from grant_management.models import Installment
from project_core.tests import database_population


class InstallmentModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_installment_valid(self):
        data = {'project': self._project,
                'due_date': datetime(2020, 1, 10),
                'amount': 200
                }

        self.assertEqual(Installment.objects.all().count(), 0)
        installment_form = InstallmentModelForm(data=data)
        self.assertTrue(installment_form.is_valid())
        installment_form.save()
        self.assertEqual(Installment.objects.all().count(), 1)

# class InstallmentsFormSetTest(TestCase):
# Currently tested from the view "unit" test
