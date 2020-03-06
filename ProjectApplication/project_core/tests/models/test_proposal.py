from datetime import datetime

from django.test import TestCase

from evaluation.models import CallEvaluation
from project_core.models import Proposal
from project_core.tests import database_population


class ProposalModelTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()

    def test_proposal_can_call_evaluation_be_visualised(self):
        proposal = Proposal(call=self._call)
        self.assertFalse(proposal.can_call_evaluation_be_visualised())

        call_evaluation = CallEvaluation(call=self._call, panel_date=datetime.now())
        call_evaluation.save()

        self.assertTrue(proposal.can_call_evaluation_be_visualised())

