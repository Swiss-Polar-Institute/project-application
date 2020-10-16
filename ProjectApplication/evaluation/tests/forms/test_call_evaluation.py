from datetime import datetime

from django.test import TestCase

from evaluation.forms.call_evaluation import CallEvaluationForm
from evaluation.models import CallEvaluation, CriterionCallEvaluation
from project_core.tests import database_population


class CallEvaluationFormTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._reviewer = database_population.create_reviewer()
        self._management_user = database_population.create_management_user()
        self._reviewer_user = database_population.create_reviewer_user()
        self._criteria = database_population.create_evaluation_criteria()

    def test_save_call_evaluation(self):
        data = {'call': self._proposal.call,
                'panel_date': datetime.today(),
                'reviewers': [self._reviewer.id],
                'criteria': [self._criteria[0].id]
                }

        self.assertEqual(CallEvaluation.objects.all().count(), 0)

        call_evaluation_form = CallEvaluationForm(data=data, call=self._proposal.call)
        self.assertTrue(call_evaluation_form.is_valid())

        self.assertRaises(PermissionError, call_evaluation_form.save_call_evaluation, self._reviewer_user)

        call_evaluation = call_evaluation_form.save_call_evaluation(self._management_user)

        self.assertEqual(CallEvaluation.objects.all().count(), 1)

        self.assertEqual(CriterionCallEvaluation.objects.filter(call_evaluation=call_evaluation).count(), 7)
        self.assertEqual(CriterionCallEvaluation.objects.filter(call_evaluation=call_evaluation, enabled=True).count(),
                         1)
        self.assertEqual(
            CriterionCallEvaluation.objects.filter(call_evaluation=call_evaluation, enabled=True)[0].criterion.id,
            self._criteria[0].id)
