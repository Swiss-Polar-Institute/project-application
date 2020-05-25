from django.test import TestCase

from project_core.forms.financial_key import FinancialKeyForm
from project_core.models import FinancialKey
from project_core.tests import database_population


class FinancialKeyTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()

    def test_financial_key_valid(self):
        data = {'name': 'PAF',
                'funding_instrument': '1',
                'description': 'Used for a funding instrument'}

        financial_key_form = FinancialKeyForm(data)

        self.assertEqual(FinancialKey.objects.all().count(), 0)
        self.assertTrue(financial_key_form.is_valid())

        # The financial key form is used this way (for the created_by required). This should
        # be tested in the FinancialKey view as well
        financial_key = financial_key_form.save(commit=False)
        financial_key.created_by = self._user
        financial_key.save()

        self.assertEqual(FinancialKey.objects.all().count(), 1)
