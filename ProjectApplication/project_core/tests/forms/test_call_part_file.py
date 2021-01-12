from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from project_core.forms.call_part_file import CallPartFileForm
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class CallPartFileTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._call_part = database_population.create_call_part(self._call)

    def test_create_call_part(self):
        call_part_file_data = dict_to_multivalue_dict({
            'name': 'form_for_logistics',
            'description': 'Please download the form and upload it later',
            'call_part': self._call_part
        })

        files = {'file': SimpleUploadedFile('form_for_logistics.docx',
                                            b'This is a good form')}

        call_part_file = CallPartFileForm(data=call_part_file_data, files=files, call_part_pk=self._call_part.pk,
                                          instance=None)
        self.assertTrue(call_part_file.is_valid())
        new_call_part = call_part_file.save()

        self.assertTrue(new_call_part.id)
        self.assertTrue(new_call_part.order, 10)
