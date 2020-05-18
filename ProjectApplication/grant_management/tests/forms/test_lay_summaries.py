from datetime import datetime

from django.test import TestCase

from ProjectApplication import settings
from grant_management.forms.lay_summaries import LaySummaryModelForm
from grant_management.models import LaySummary, LaySummaryType
from project_core.tests import database_population


class LaySummaryModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_lay_summary_valid(self):
        LaySummaryType.objects.get_or_create(name=settings.LAY_SUMMARY_ORIGINAL, description='Original')

        data = {'project': self._project,
                'lay_summary_type': LaySummaryType.objects.get(name=settings.LAY_SUMMARY_ORIGINAL),
                'due_date': datetime(2020, 1, 10),
                'received_date': datetime(2020, 1, 10),
                'text': 'This is the text of the lay summary',
                'author': self._project.principal_investigator.person
                }

        self.assertEqual(LaySummary.objects.all().count(), 0)
        lay_summary_form = LaySummaryModelForm(data=data)
        self.assertTrue(lay_summary_form.is_valid())
        lay_summary_form.save()
        self.assertEqual(LaySummary.objects.all().count(), 1)
