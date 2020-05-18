from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from grant_management.forms.media import MediumModelForm
from grant_management.models import Medium, License
from project_core.tests import database_population


class MediumModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_medium_valid(self):
        file = SimpleUploadedFile('photography.jpg',
                                  b'This should contain a JPEG for example.')
        license, _ = License.objects.get_or_create(name='Creative Commons', spdx_identifier='cc')

        data = {'project': self._project,
                'received_date': datetime(2020, 1, 1),
                'photographer': self._project.principal_investigator.person,
                'license': license
                }

        file = {'file': file}

        self.assertEqual(Medium.objects.all().count(), 0)
        medium_form = MediumModelForm(data=data, files=file, project=self._project)
        self.assertTrue(medium_form.is_valid())
        medium_form.save()
        self.assertEqual(Medium.objects.all().count(), 1)
