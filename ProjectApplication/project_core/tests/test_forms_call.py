from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from ..forms.call import CallForm


def values_as_list(d):
    result = dict()

    for key, value in d.items():
        result[key] = [value]

    return result


class CallFormTest(TestCase):
    fixtures = ['basic.json', ]

    def test_deadline(self):
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
        # self.assertTrue(call_form.is_valid())
        print(call_form.errors)
        self.assertTrue(call_form.is_valid())
