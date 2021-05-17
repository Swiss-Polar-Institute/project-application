from django.test import TestCase

from project_core.tests import database_population
from ..models import Invoice, Installment


class InvoiceTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def installment_number_test(self):
        installment = Installment.objects.create(project=self._project,
                                                 due_date=self._project.end_date,
                                                 amount=200)

        invoice = Invoice.objects.create(project=self._project,
                                         installment=installment,
                                         due_date=self._project.end_date,
                                         amount=200)

        self.assertEqual(invoice.installment_number(), 1)

    def installment_number_none_test(self):
        invoice = Invoice.objects.create(project=self._project,
                                         installment=None,
                                         due_date=self._project.end_date,
                                         amount=200)

        self.assertIsNone(invoice.installment_number())

