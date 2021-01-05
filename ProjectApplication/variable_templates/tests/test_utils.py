import unittest
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
        utils.get_template_value_for_call('activity', self._call)

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

        utils.apply_templates_to_fields(fields, self._call)

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

        utils.apply_templates_to_fields(fields, self._call)

        self.assertNotIn('{{ activity }}', fields['title'].help_text)

        self.assertEqual('Name of the party', fields['title'].help_text)

    def test_apply_templates(self):
        title_field = forms.CharField(label='Name', help_text='Name of the {{ activity }}')
        keywords_field = forms.CharField(label='Keywords', help_text='List the keywords')

        fields = OrderedDict({'title': title_field,
                              'keywords': keywords_field
                              })

        self.assertIn('{{ activity }}', fields['title'].help_text)

        utils.apply_templates_to_fields(fields, self._call)

        self.assertNotIn('{{ activity }}', fields['title'].help_text)
        self.assertEqual('Name of the proposal', fields['title'].help_text)

    def get_template_value_for_funding_instrument_from_default_test(self):
        activity = utils.get_template_value_for_funding_instrument('activity', self._funding_instrument)
        self.assertEqual(activity, 'proposal')

    def get_template_value_for_funding_instrument_from_funding_instrument(self):
        template_variable_name = TemplateVariableName.objects.get(name='activity')
        FundingInstrumentVariableTemplate.objects.create(name=template_variable_name,
                                                         value='dish',
                                                         funding_instrument=self._funding_instrument)

        activity = utils.get_template_value_for_funding_instrument('activity', self._funding_instrument)
        self.assertEqual(activity, 'dish')

    def test_copy_template_variables_from_funding_instrument_to_call_test(self):
        template_variable_name = TemplateVariableName.objects.get(name='activity')
        FundingInstrumentVariableTemplate.objects.create(funding_instrument=self._funding_instrument,
                                                         name=template_variable_name,
                                                         value='proposal')

        self.assertEqual(self._call.callvariabletemplate_set.all().count(), 0)
        utils.copy_template_variables_from_funding_instrument_to_call(self._call)
        self.assertEqual(self._call.callvariabletemplate_set.all().count(), 1)
        self.assertTrue(self._call.callvariabletemplate_set.get(name=template_variable_name, value='proposal'))

    def test_get_template_value_for_funding_instrument_test(self):
        activity = utils.get_template_value_for_funding_instrument('activity', self._funding_instrument)
        self.assertEqual(activity, 'proposal')

    @unittest.expectedFailure
    def test_get_template_value_for_funding_instrument_test_does_not_exist(self):
        utils.get_template_value_for_funding_instrument('does_not_exist', self._funding_instrument)

    def test_get_template_value_for_call(self):
        activity = utils.get_template_value_for_call('activity', self._call)
        self.assertEqual(activity, 'proposal')

    @unittest.expectedFailure
    def test_get_template_value_for_call_does_not_exist(self):
        utils.get_template_value_for_call('does_not_exist', self._call)
