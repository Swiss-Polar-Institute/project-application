from collections import OrderedDict

from django import forms
from django.test import TestCase

from project_core.tests import database_population as project_core_database_population
from . import database_population
from .. import utils


# class Field:
#     def __init__(self):
#         self.help_text = None
#         self.label = None
#
#     pass

class UtilsTest(TestCase):
    def setUp(self):
        self._call = project_core_database_population.create_call()
        database_population.create_default_variables()

    def test_get_template_value(self):
        utils.get_template_value('activity', self._call)

    def test_apply_templates(self):
        title_field = forms.CharField(label='Name', help_text='Name of the {{ activity }}')
        keywords_field = forms.CharField(label='Keywords', help_text='List the keywords')

        fields = OrderedDict({'title': title_field,
                              'keywords': keywords_field
                              })

        self.assertIn('{{ activity }}', fields['title'].help_text)

        utils.apply_templates(fields, self._call)

        self.assertNotIn('{{ activity }}', fields['title'].help_text)
