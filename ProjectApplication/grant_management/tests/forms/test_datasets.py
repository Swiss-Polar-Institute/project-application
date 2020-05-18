from datetime import datetime

from django.test import TestCase

from grant_management.forms.datasets import DatasetModelForm
from grant_management.models import Dataset
from project_core.tests import database_population


class DatasetModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_dataset_valid(self):
        data = {'project': self._project,
                'doi': 'doi:24294213',
                'url': 'https://zenodo.org/something',
                'title': 'A very interesting dataset',
                'published_date': datetime(2020, 5, 18),
                }

        self.assertEqual(Dataset.objects.all().count(), 0)
        dataset_form = DatasetModelForm(data=data)
        self.assertTrue(dataset_form.is_valid())
        dataset_form.save()
        self.assertEqual(Dataset.objects.all().count(), 1)
