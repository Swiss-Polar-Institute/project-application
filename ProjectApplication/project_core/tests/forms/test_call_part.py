from django.test import TestCase

from project_core.forms.call_part import CallPartForm
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class CallPartFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()

    def test_create_call_part(self):
        call_part_data = dict_to_multivalue_dict(
            {'call': self._call,
             'title': 'Weather information',
             'introductory_text': 'Please explain weather information that might be important during the expedition'
             })

        call_part_form = CallPartForm(data=call_part_data, call_pk=self._call.pk, instance=None)
        self.assertTrue(call_part_form.is_valid())
        new_call_part = call_part_form.save()

        self.assertTrue(new_call_part.id)
        self.assertTrue(new_call_part.order, 10)
