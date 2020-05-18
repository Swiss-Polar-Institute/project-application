from django.test import TestCase

from grant_management.forms.project import ProjectForm
from project_core.tests import database_population


class ProjectFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_project_valid(self):
        geographical_area_ids = list(self._project.geographical_areas.all().values_list('id', flat=True))
        keyword_ids = list(self._project.keywords.all().values_list('id', flat=True))

        data = {'title': 'New Title v 2.0',
                'keywords': keyword_ids,
                'geographical_areas': geographical_area_ids,
                'location': 'This is a new location',
                'start_date': self._project.start_date,
                'end_date': self._project.end_date
                }

        project_form = ProjectForm(data=data, instance=self._project)
        self.assertTrue(project_form.is_valid())
        project_form.save()
        self._project.refresh_from_db()
        self.assertEqual(self._project.title, 'New Title v 2.0')
        self.assertEqual(self._project.location, 'This is a new location')
