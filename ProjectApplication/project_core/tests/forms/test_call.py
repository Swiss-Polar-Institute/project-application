import datetime

from django.test import TestCase

from project_core.forms.call import CallForm
from project_core.tests import database_population
from project_core.tests.utils import dict_to_multivalue_dict


class CallFormTest(TestCase):
    def setUp(self):
        self._budget_categories = database_population.create_budget_categories()
        self._template_questions = database_population.create_template_questions()

    def test_call(self):
        call_data = dict_to_multivalue_dict(
            {'call_open_date': '01-01-2020 10:00',
             'submission_deadline': (datetime.datetime.now() + datetime.timedelta(days=10)).strftime('%d-%m-%Y 12:00'),
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data.setlist('budget_categories',
                          [self._budget_categories[0].id, self._budget_categories[1].id])

        call_form = CallForm(data=call_data)
        self.assertTrue(call_form.is_valid())
        new_call = call_form.save()

        self.assertTrue(new_call.id)

    def test_deadline_too_early(self):
        call_data = dict_to_multivalue_dict(
            {'call_open_date': '15-01-2022 10:00',
             'submission_deadline': '01-01-2022 12:00',
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data.setlist('budget_categories', [self._budget_categories[0], self._budget_categories[1]])

        call_data.setlist('template_questions', [self._template_questions[0]])

        call_form = CallForm(data=call_data)
        self.assertFalse(call_form.is_valid())

        self.assertEqual(call_form.errors['call_open_date'],
                         ['Call open date needs to be before the submission deadline'])
