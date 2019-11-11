from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from project_core.forms.call import CallForm


def values_as_list(d):
    result = dict()

    for key, value in d.items():
        result[key] = [value]

    return result


class CallFormTest(TestCase):
    fixtures = ['basic.json', ]

    def test_call(self):
        call_data = values_as_list(
            {'call_open_date_0': '2020-01-01',
             'call_open_date_1': '10:00',
             'submission_deadline_0': '2020-01-31',
             'submission_deadline_1': '12:00',
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data = MultiValueDict(call_data)

        call_data.setlist('budget_categories', ['2', '3'])

        call_form = CallForm(data=call_data)
        self.assertTrue(call_form.is_valid())

    def test_deadline_too_early(self):
        call_data = values_as_list(
            {'call_open_date_0': '2022-01-15',
             'call_open_date_1': '10:00',
             'submission_deadline_0': '2022-01-01',
             'submission_deadline_1': '12:00',
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data = MultiValueDict(call_data)

        call_data.setlist('budget_categories', ['2', '3'])

        call_form = CallForm(data=call_data)
        self.assertFalse(call_form.is_valid())

        self.assertEqual(call_form.errors['call_open_date'],
                         ['Call open date needs to be before the submission deadline'])
