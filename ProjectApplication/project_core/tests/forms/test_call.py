from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from project_core.forms.call import CallForm
from project_core.models import BudgetCategory, TemplateQuestion
from project_core.tests import database_population
from project_core.tests.utils import dict_to_multivalue_dict


class CallFormTest(TestCase):
    def setUp(self):
        database_population.create_budget_categories()
        database_population.create_template_questions()

    def test_call(self):
        call_data = dict_to_multivalue_dict(
            {'call_open_date_0': '2020-01-01',
             'call_open_date_1': '10:00',
             'submission_deadline_0': '2020-01-31',
             'submission_deadline_1': '12:00',
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data.setlist('budget_categories',
                          [BudgetCategory.objects.get(name='Travel').id,
                           BudgetCategory.objects.get(name='Data processing').id])

        call_form = CallForm(data=call_data)
        self.assertTrue(call_form.is_valid())
        new_call = call_form.save()

        self.assertTrue(new_call.id)

    def test_deadline_too_early(self):
        call_data = dict_to_multivalue_dict(
            {'call_open_date_0': '2022-01-15',
             'call_open_date_1': '10:00',
             'submission_deadline_0': '2022-01-01',
             'submission_deadline_1': '12:00',
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data.setlist('budget_categories',
                          [BudgetCategory.objects.get(name='Travel').id,
                           BudgetCategory.objects.get(name='Data processing').id])

        call_data.setlist('template_questions', [
            TemplateQuestion.objects.get(
                question_text='Explain which methods of transport are needed to go to the location')])

        call_form = CallForm(data=call_data)
        self.assertFalse(call_form.is_valid())

        self.assertEqual(call_form.errors['call_open_date'],
                         ['Call open date needs to be before the submission deadline'])
