from django.test import TestCase

from grant_management.forms.fieldnotes import FieldNoteModelForm
from grant_management.models import FieldNote
from project_core.tests import database_population


class FieldNoteModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_fieldnote_valid(self):
        data = {'project': self._project,
                'url': 'https://test.org/something',
                'title': 'A very interesting fieldnote',
                }

        self.assertEqual(FieldNote.objects.all().count(), 0)
        fieldnote_form = FieldNoteModelForm(data=data)
        self.assertTrue(fieldnote_form.is_valid())
        fieldnote_form.save()
        self.assertEqual(FieldNote.objects.all().count(), 1)
