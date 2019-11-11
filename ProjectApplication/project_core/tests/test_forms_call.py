from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from ..forms.call import CallForm


def dict_to_multivalue_dict(d):
    multi_value_dict = MultiValueDict()

    for key, value in d.items():
        multi_value_dict[key] = [value]

    return multi_value_dict


class CallFormTest(TestCase):
    def test_deadline(self):
        call_data = MultiValueDict(
            {'call_open_date_0': ['2020-01-01'],
             'call_open_date_1': ['10:00'],
             'submission_deadline_0': ['2020-01-31'],
             'submission_deadline_1': ['12:00'],
             'long_name': ['GreenLAnd Circumnavigation Expedition'],
             'description': ['Cool, cold'],
             'budget_maximum': [100_000],
             'budget_categories': [1, 3, 5]
             }
        )

        # call_data = dict_to_multivalue_dict(call_data)
        # call_data['budget_categories'] = [1, 4, 5]
        call_form = CallForm(data=call_data)
        # self.assertTrue(call_form.is_valid())
        call_form.is_valid()
        print('test')
