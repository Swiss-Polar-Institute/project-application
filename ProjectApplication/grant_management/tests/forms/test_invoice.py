from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from grant_management.forms.invoices import InvoiceItemModelForm
from grant_management.models import GrantAgreement, Invoice
from project_core.tests import database_population


class InvoiceItemFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_valid_incomplete_invoice(self):
        data = {'project': self._project,
                'due_date': date(2020, 1, 12)
                }

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data)

        self.assertTrue(invoice_item_form.is_valid())
        invoice_item_form.save()
        self.assertEqual(Invoice.objects.all().count(), 1)

    def test_valid_empty_invoice_no_save(self):
        data = {'project': self._project}

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data)

        self.assertTrue(invoice_item_form.is_valid())
        invoice_item_form.save()
        self.assertEqual(Invoice.objects.all().count(), 0)

    def test_valid_complete_invoice(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 12),
                                         signed_by=database_population.create_physical_person(),
                                         file=SimpleUploadedFile('grant_agreement.txt',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()

        data = {'project': self._project,
                'due_date': date(2020, 1, 13),
                'received_date': date(2020, 1, 14),
                'sent_date': date(2020, 1, 15),
                'amount': 200,
                'paid_date': date(2020, 1, 16)
                }
        file = {'file': SimpleUploadedFile('file.txt', b'some file content')}

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data, files=file)

        self.assertTrue(invoice_item_form.is_valid())
        invoice_item_form.save()
        self.assertEqual(Invoice.objects.all().count(), 1)

    def test_invalid_due_date_too_early(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 4),
                                         signed_by=database_population.create_physical_person(),
                                         file=SimpleUploadedFile('grant_agreement.txt',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()

        data = {'project': self._project,
                'due_date': date(2019, 12, 1),
                }

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data)

        invoice_item_form.is_valid()
        self.assertFalse(invoice_item_form.is_valid())
        self.assertIn('due_date', invoice_item_form.errors)

    def test_invalid_due_date_too_late(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 4),
                                         signed_by=database_population.create_physical_person(),
                                         file=SimpleUploadedFile('grant_agreement.txt',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()

        data = {'project': self._project,
                'due_date': date(2025, 12, 1),
                }

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data)

        invoice_item_form.is_valid()
        self.assertFalse(invoice_item_form.is_valid())
        self.assertIn('due_date', invoice_item_form.errors)

    def test_invalid_amount_missing(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 4),
                                         signed_by=database_population.create_physical_person(),
                                         file=SimpleUploadedFile('grant_agreement.txt',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()

        data = {'project': self._project,
                'due_date': date(2020, 1, 5),
                'received_date': date(2020, 1, 6),
                'sent_for_payment_date': date(2020, 1, 7),
                'paid_date': date(2020, 1, 8)
                }
        file = {'file': SimpleUploadedFile('file.txt', b'some file content')}

        invoice_item_form = InvoiceItemModelForm(data=data, files=file)

        self.assertFalse(invoice_item_form.is_valid())
        self.assertIn('amount', invoice_item_form.errors)

    def test_invalid_grant_management_missing(self):
        data = {'project': self._project,
                'due_date': date(2020, 1, 5),
                'received_date': date(2020, 1, 6),
                'sent_for_payment_date': date(2020, 1, 7),
                }

        invoice_item_form = InvoiceItemModelForm(data=data)

        self.assertFalse(invoice_item_form.is_valid())
        # sent_date cannot be entered because the grant agreement is not signed
        self.assertIn('sent_for_payment_date', invoice_item_form.errors)
