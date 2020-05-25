from django.test import TestCase

from project_core.tests import database_population
from variable_templates.forms.template_variables import TemplateVariableItemForm
from variable_templates.models import CallVariableTemplate, TemplateVariableName


class TemplateVariableItemFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()

    def save_into_funding_instrument_test(self):
        template_variable_name, _ = TemplateVariableName.objects.get_or_create(name='activity', default='proposal')
        call_variable_template, _ = CallVariableTemplate.objects.get_or_create(call=self._call,
                                                                               name=template_variable_name,
                                                                               value='proposal2')

        data = {'name': template_variable_name.id,
                'value': 'proposal'
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

        self.assertEqual(self._call.callvariabletemplate_set.all().count(), 1)
