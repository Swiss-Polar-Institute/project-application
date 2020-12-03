import datetime

from django.test import TestCase

from project_core.forms.call import CallForm, CallQuestionItemForm
from project_core.models import CallQuestion
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class CallFormTest(TestCase):
    def setUp(self):
        self._budget_categories = database_population.create_budget_categories()
        self._template_questions = database_population.create_template_questions()

    def test_create_call(self):
        funding_instrument = database_population.create_funding_instrument()

        call_data = dict_to_multivalue_dict(
            {'call_open_date': '01-01-2020 10:00',
             'submission_deadline': (datetime.datetime.now() + datetime.timedelta(days=10)).strftime('%d-%m-%Y 12:00'),
             'finance_year': 2020,
             'long_name': 'GreenLAnd Circumnavigation Expedition 2',
             'description': 'Cool, cold',
             'budget_maximum': '100000',
             }
        )

        call_data.setlist('budget_categories',
                          [self._budget_categories[0].id, self._budget_categories[1].id])
        call_data.setlist('funding_instrument', [funding_instrument.id])

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

        call_data.setlist('budget_categories', [self._budget_categories[0].id, self._budget_categories[1].id])

        call_data.setlist('template_questions', [self._template_questions[0]])

        call_form = CallForm(data=call_data)
        self.assertFalse(call_form.is_valid())

        self.assertEqual(call_form.errors['call_open_date'],
                         ['Call open date needs to be before the submission deadline'])


class CallQuestionItemFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._template_questions = database_population.create_template_questions()

    def test_create_question_item_form(self):
        call_question = CallQuestion.objects.create(question_text='Original question',
                                                    question_description='Original template question description',
                                                    answer_max_length=50,
                                                    answer_required=False,
                                                    call=self._call,
                                                    template_question=self._template_questions[0])

        data = {'id': str(call_question.id),
                'order': '1',
                'question_text': 'Please write how do you plan to go to your destination.',
                'question_description': 'This is in order to understand how do you plan to go',
                'answer_max_length': '100',
                'answer_required': 'on',
                }

        call_question_item_form = CallQuestionItemForm(data)

        self.assertEqual(CallQuestion.objects.all().count(), 1)
        call_question = call_question_item_form.save(False)

        self.assertEqual(call_question.question_text, 'Please write how do you plan to go to your destination.')
        self.assertEqual(call_question.question_description, 'This is in order to understand how do you plan to go')
        self.assertEqual(call_question.answer_max_length, 100)
        self.assertEqual(call_question.answer_required, True)
