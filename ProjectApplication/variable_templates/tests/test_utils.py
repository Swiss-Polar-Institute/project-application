from collections import OrderedDict

from django import forms
from django.test import TestCase

from project_core.tests import database_population as project_core_database_population
from . import database_population
from .. import utils
from ..models import CallVariableTemplate, TemplateVariableName, FundingInstrumentVariableTemplate


class UtilsTest(TestCase):
    def setUp(self):
        self._funding_instrument = project_core_database_population.create_funding_instrument()
        self._call = project_core_database_population.create_call(self._funding_instrument)

        database_population.delete_all_variables()
        database_population.create_default_variables()

    def test_get_template_value(self):
        utils.get_template_value('activity', self._call)

    def test_apply_templates_funding_from_funding_instrument(self):
        template = TemplateVariableName.objects.get(name='activity')
        FundingInstrumentVariableTemplate.objects.get_or_create(funding_instrument=self._funding_instrument,
                                                                name=template,
                                                                value='party')

        title_field = forms.CharField(label='Name', help_text='Name of the {{ activity }}')
        keywords_field = forms.CharField(label='Keywords', help_text='List the keywords')

        fields = OrderedDict({'title': title_field,
                              'keywords': keywords_field
                              })

        self.assertIn('{{ activity }}', fields['title'].help_text)

        utils.apply_templates(fields, self._call)

        self.assertNotIn('{{ activity }}', fields['title'].help_text)

        self.assertEqual('Name of the party', fields['title'].help_text)

    def test_apply_templates_funding_from_call(self):
        template = TemplateVariableName.objects.get(name='activity')
        CallVariableTemplate.objects.get_or_create(call=self._call, name=template, value='party')

        title_field = forms.CharField(label='Name', help_text='Name of the {{ activity }}')
        keywords_field = forms.CharField(label='Keywords', help_text='List the keywords')

        fields = OrderedDict({'title': title_field,
                              'keywords': keywords_field
                              })

        self.assertIn('{{ activity }}', fields['title'].help_text)

        utils.apply_templates(fields, self._call)

        self.assertNotIn('{{ activity }}', fields['title'].help_text)

        self.assertEqual('Name of the party', fields['title'].help_text)

    def test_apply_templates(self):
        title_field = forms.CharField(label='Name', help_text='Name of the {{ activity }}')
        keywords_field = forms.CharField(label='Keywords', help_text='List the keywords')

        fields = OrderedDict({'title': title_field,
                              'keywords': keywords_field
                              })

        self.assertIn('{{ activity }}', fields['title'].help_text)

        utils.apply_templates(fields, self._call)

        self.assertNotIn('{{ activity }}', fields['title'].help_text)
        self.assertEqual('Name of the proposal', fields['title'].help_text)
