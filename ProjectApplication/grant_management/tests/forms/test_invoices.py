from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from grant_management.forms.invoices import InvoiceItemModelForm
from grant_management.models import GrantAgreement, Invoice, LaySummary
from project_core.tests import database_population


class InvoiceItemFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._user = database_population.create_management_user()
        self._lay_summary_original_type = database_population.create_lay_summary_original()

    def _create_invoice_form(self, amount, allow_overbudget=None):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 12),
                                         file=SimpleUploadedFile('grant_agreement.pdf',
                                                                 b'This is the signed grant agreement. C.'))

        grant_agreement.save()

        grant_agreement.signed_by.set([database_population.create_physical_person()])

        lay_summary = LaySummary(project=self._project,
                                 due_date=date(2020, 1, 13),
                                 text='test',
                                 author=self._project.principal_investigator.person,
                                 lay_summary_type=self._lay_summary_original_type)
        lay_summary.save()

        data = {'test-due_date': date(2020, 1, 13),
                'test-received_date': date(2020, 1, 14),
                'test-sent_for_payment_date': date(2020, 1, 15),
                'test-amount': amount,
                'test-paid_date': date(2020, 1, 16)
                }

        if allow_overbudget is not None:
            data['test-allow_overbudget'] = allow_overbudget

        file = {'test-file': SimpleUploadedFile('file.pdf', b'some file content')}

        return InvoiceItemModelForm(data=data, files=file, user=self._user, project=self._project, prefix='test')

    def test_valid_complete_invoice(self):
        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = self._create_invoice_form(amount=200)

        self.assertNotIn('allow_overbudget', invoice_item_form.fields)

        self.assertTrue(invoice_item_form.is_valid())
        invoice = invoice_item_form.save()
        self.assertEqual(Invoice.objects.all().count(), 1)

        self.assertEqual(invoice.amount, 200)

    def test_valid_due_date_earlier_project_starts(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 4),
                                         file=SimpleUploadedFile('grant_agreement.pdf',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()
        grant_agreement.signed_by.set([database_population.create_physical_person()])

        data = {'project': self._project,
                'due_date': date(2019, 12, 1),
                }

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data, project=self._project)

        invoice_item_form.is_valid()
        self.assertTrue(invoice_item_form.is_valid())
        # self.assertIn('due_date', invoice_item_form.errors)

    def test_invalid_due_date_too_late(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 4),
                                         file=SimpleUploadedFile('grant_agreement.pdf',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()

        grant_agreement.signed_by.set([database_population.create_physical_person()])

        data = {'project': self._project,
                'due_date': date(2025, 12, 1),
                }

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data, project=self._project)

        invoice_item_form.is_valid()
        self.assertFalse(invoice_item_form.is_valid())
        self.assertIn('due_date', invoice_item_form.errors)

    def test_invalid_amount_missing(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 4),
                                         file=SimpleUploadedFile('grant_agreement.pdf',
                                                                 b'This is the signed grant agreement. C.'))
        grant_agreement.save()
        grant_agreement.signed_by.set([database_population.create_physical_person()])

        data = {'project': self._project,
                'due_date': date(2020, 1, 5),
                'received_date': date(2020, 1, 6),
                'sent_for_payment_date': date(2020, 1, 7),
                'paid_date': date(2020, 1, 8)
                }
        file = {'file': SimpleUploadedFile('file.pdf', b'some file content')}

        invoice_item_form = InvoiceItemModelForm(data=data, files=file, project=self._project)

        self.assertFalse(invoice_item_form.is_valid())
        self.assertIn('amount', invoice_item_form.errors)

    def test_invalid_grant_management_missing(self):
        data = {'project': self._project,
                'due_date': date(2020, 1, 5),
                'received_date': date(2020, 1, 6),
                'sent_for_payment_date': date(2020, 1, 7),
                }

        invoice_item_form = InvoiceItemModelForm(data=data, project=self._project)

        self.assertFalse(invoice_item_form.is_valid())
        # sent_date cannot be entered because the grant agreement is not signed
        self.assertIn('sent_for_payment_date', invoice_item_form.errors)

    def test_invalid_invoice_amount_bigger_than_project(self):
        grant_agreement = GrantAgreement(project=self._project,
                                         signed_date=date(2020, 1, 12),
                                         file=SimpleUploadedFile('grant_agreement.pdf',
                                                                 b'This is the signed grant agreement. C.'))

        grant_agreement.save()

        grant_agreement.signed_by.set([database_population.create_physical_person()])

        lay_summary = LaySummary(project=self._project,
                                 due_date=date(2020, 1, 13),
                                 text='test',
                                 author=self._project.principal_investigator.person,
                                 lay_summary_type=self._lay_summary_original_type)
        lay_summary.save()

        data = {'due_date': date(2020, 1, 13),
                'received_date': date(2020, 1, 14),
                'sent_for_payment_date': date(2020, 1, 15),
                'amount': 25_000,
                'paid_date': date(2020, 1, 16)
                }
        file = {'file': SimpleUploadedFile('file.pdf', b'some file content')}

        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = InvoiceItemModelForm(data=data, files=file, user=self._user, project=self._project)

        self.assertFalse(invoice_item_form.is_valid())
        self.assertIn('amount', invoice_item_form.errors)

    def test_valid_invoice_amount_bigger_than_project_check(self):
        self.assertEqual(Invoice.objects.all().count(), 0)
        invoice_item_form = self._create_invoice_form(amount=25_000, allow_overbudget=True)

        self.assertIn('allow_overbudget', invoice_item_form.fields)

        self.assertTrue(invoice_item_form.is_valid())
        invoice = invoice_item_form.save()
        self.assertEqual(Invoice.objects.all().count(), 1)

        self.assertEqual(invoice.amount, 25_000)
        self.assertEqual(invoice.project.allocated_budget, 20_000)

# InvoicesFormSet tested via the view