from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from project_core.models import CallPartFile
from project_core.tests import database_population


class CallPartFileTest(TestCase):
    def setUp(self):
        self._client_management = database_population.create_management_logged_client()

        self._call = database_population.create_call()
        self._call_part = database_population.create_call_part(self._call)
        self._call_part_file = database_population.create_call_part_file(self._call_part)

    def test_list(self):
        response = self._client_management.get(
            reverse('logged-call-part-file-list', kwargs={'call_pk': self._call.pk,
                                                          'call_part_pk': self._call_part.pk
                                                          }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call_part_file.name)

    def test_detail(self):
        response = self._client_management.get(
            reverse('logged-call-part-file-detail', kwargs={'call_pk': self._call.pk,
                                                            'call_file_pk': self._call_part_file.pk
                                                            }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self._call_part_file.name)

    def test_delete(self):
        call_part_file, created = CallPartFile.objects.get_or_create(file=SimpleUploadedFile('form_to_download2.docx',
                                                                                             b'Some form to download2'),
                                                                     call_part=self._call_part,
                                                                     name='Form to download2'
                                                                     )

        response = self._client_management.post(reverse('logged-call-part-file-delete'),
                                                data={'fileId': call_part_file.pk, 'partId': self._call_part.id})

        self.assertEqual(response.status_code, 302)

        self.assertRaises(ObjectDoesNotExist, call_part_file.refresh_from_db)
