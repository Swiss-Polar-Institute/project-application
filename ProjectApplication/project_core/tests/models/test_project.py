import datetime

from django.test import TestCase

from grant_management.models import Invoice
from project_core.tests import database_population


class ProjectModelTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_project_invoices_sent_for_payment(self):
        self.assertEqual(self._project.invoices_sent_for_payment_amount(), 0)

        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               sent_for_payment_date=datetime.date.today(),
                               paid_date=datetime.date.today(),
                               amount=2_000)

        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               sent_for_payment_date=datetime.date.today(),
                               amount=1_500)

        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               sent_for_payment_date=datetime.date.today(),
                               paid_date=datetime.date.today(),
                               amount=-200)

        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               amount=1_000)

        self.assertEqual(self._project.invoices_sent_for_payment_amount(), 3_300)

    def test_project_invoices_paid(self):
        self.assertEqual(self._project.invoices_paid_amount(), 0)

        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               sent_for_payment_date=datetime.date.today(),
                               paid_date=datetime.date.today(),
                               amount=2_000)

        # Next invoice is not paid
        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               sent_for_payment_date=datetime.date.today(),
                               amount=1_500)

        Invoice.objects.create(project=self._project,
                               received_date=datetime.date.today(),
                               sent_for_payment_date=datetime.date.today(),
                               paid_date=datetime.date.today(),
                               amount=-200)

        self.assertEqual(self._project.invoices_paid_amount(), 1_800)
