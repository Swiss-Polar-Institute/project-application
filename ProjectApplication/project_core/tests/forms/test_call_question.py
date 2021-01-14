from django.test import TestCase

from project_core.forms.call_question import CallQuestionForm
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class CallQuestionFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._call_part = database_population.create_call_part(self._call)

    def test_create_call_part(self):
        call_question = database_population.create_call_question(self._call_part)

        new_question_text = 'How far will you walk - edited?'

        call_question_data = dict_to_multivalue_dict(
            {'call': self._call,
             'call_part': self._call_part,
             'question_text': new_question_text,
             'question_description': 'In meters please',
             'order': 10
             })

        call_question_form = CallQuestionForm(data=call_question_data, instance=call_question, call_part_pk=self._call_part.pk)
        self.assertTrue(call_question_form.is_valid())
        call_question = call_question_form.save()

        call_question.refresh_from_db()

        self.assertEqual(call_question.question_text, new_question_text)
