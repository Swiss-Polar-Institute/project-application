from django.test import TestCase

from project_core.tests import database_population
from variable_templates.forms.template_variables import TemplateVariableItemForm
from variable_templates.models import CallVariableTemplate, TemplateVariableName, FundingInstrumentVariableTemplate


class TemplateVariableItemFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._funding_instrument = self._call.funding_instrument

    def test_save_into_call_test(self):
        template_variable_name, _ = TemplateVariableName.objects.get_or_create(name='activity', default='proposal')
        call_variable_template, _ = CallVariableTemplate.objects.get_or_create(call=self._call,
                                                                               name=template_variable_name,
                                                                               value='proposal2')

        data = {'name': template_variable_name.id,
                'value': 'dish'
                }

        initial = {'id': None,
                   'current_value': 'project',
                   'template_variable': template_variable_name,
                   'value': 'dish'
                   }

        template_variable_item_form = TemplateVariableItemForm(data=data, initial=initial)

        self.assertTrue(template_variable_item_form.is_valid())

        self.assertEqual(self._call.callvariabletemplate_set.all().count(), 1)

        template_variable_item_form.save_template_variable_into_call(self._call)
        self._call.refresh_from_db()
        self.assertEqual(self._call.callvariabletemplate_set.all().count(), 1)
        self.assertEqual(self._call.callvariabletemplate_set.all()[0].value, 'dish')

    def test_save_into_funding_instrument_test(self):
        template_variable_name, _ = TemplateVariableName.objects.get_or_create(name='activity', default='proposal')
        funding_instrument_variable_template, _ = FundingInstrumentVariableTemplate.objects.get_or_create(
            funding_instrument=self._funding_instrument,
            name=template_variable_name,
            value='proposal2')

        data = {'name': template_variable_name.id,
                'value': 'dish'
                }

        initial = {'id': None,
                   'current_value': 'project',
                   'template_variable': template_variable_name,
                   'value': 'dish'
                   }

        template_variable_item_form = TemplateVariableItemForm(data=data, initial=initial)

        self.assertTrue(template_variable_item_form.is_valid())

        self.assertEqual(self._funding_instrument.fundinginstrumentvariabletemplate_set.all().count(), 1)

        template_variable_item_form.save_template_variable_into_funding_instrument(self._funding_instrument)
        self._funding_instrument.refresh_from_db()
        self.assertEqual(self._funding_instrument.fundinginstrumentvariabletemplate_set.all().count(), 1)
        self.assertEqual(self._funding_instrument.fundinginstrumentvariabletemplate_set.all()[0].value, 'dish')
