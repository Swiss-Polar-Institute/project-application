from django.test import TestCase

from grant_management.forms.close_project import CloseProjectModelForm
from project_core.models import Project
from project_core.tests import database_population


class CloseProjectFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_aborted(self):
        data = {'status': 'Aborted',
                'abortion_reason': 'Permit did not arrive on time',
                'close': 'Close'
                }

        self.assertEqual(self._project.status, Project.ONGOING)

        close_project_form = CloseProjectModelForm(data=data, instance=self._project)

        self.assertTrue(close_project_form.is_valid())

        close_project_form.save()

        self.assertEqual(self._project.status, Project.ABORTED)

    def test_completed(self):
        data = {'status': 'Completed',
                'abortion_reason': '',
                'close': 'Close'
                }

        self.assertEqual(self._project.status, Project.ONGOING)

        close_project_form = CloseProjectModelForm(data=data, instance=self._project)

        self.assertTrue(close_project_form.is_valid())

        close_project_form.save()

        self.assertEqual(self._project.status, Project.COMPLETED)
