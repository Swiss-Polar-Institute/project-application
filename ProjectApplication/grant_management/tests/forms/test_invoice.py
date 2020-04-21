from datetime import datetime
from io import StringIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from grant_management.forms.invoices import InvoiceItemModelForm
from project_core.tests import database_population


class InvoiceItemFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_valid_incomplete_invoice(self):
        data = {'project': self._project,
                'due_date': datetime(2020, 1, 5)
                }

        invoice_item_form = InvoiceItemModelForm(data=data)

        self.assertTrue(invoice_item_form.is_valid())

    def test_valid_complete_invoice(self):
        data = {'project': self._project,
                'due_date': datetime(2020, 1, 5),
                'reception_date': datetime(2020, 1, 6),
                }
        file = {'file': SimpleUploadedFile('file.txt', b'some file content')}

        invoice_item_form = InvoiceItemModelForm(data=data, files=file)

        self.assertTrue(invoice_item_form.is_valid())
