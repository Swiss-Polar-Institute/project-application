from datetime import datetime

from django.test import TestCase

from ProjectApplication import settings
from evaluation.models import CallEvaluation
from project_core.models import Proposal, ProposalStatus
from project_core.tests import database_population


class ProposalModelTest(TestCase):
    def setUp(self):
        self._proposal_status_submitted, _ = ProposalStatus.objects.get_or_create(
            name=settings.PROPOSAL_STATUS_SUBMITTED)

    def test_proposal_can_create_evaluation(self):
        proposal = database_population.create_proposal()

        # It cannot be evaluated, it's not eligible
        self.assertFalse(proposal.can_create_evaluation())
        self.assertEqual('To evaluate the proposal the status needs to be submitted',
                         proposal.reason_cannot_create_evaluation())

        # Let's make it eligible
        proposal.eligibility = Proposal.ELIGIBLE
        proposal.save()

        # It cannot be evaluated: the proposal status needs to be submitted
        self.assertFalse(proposal.can_create_evaluation())
        self.assertEqual('To evaluate the proposal the status needs to be submitted',
                         proposal.reason_cannot_create_evaluation())

        # Let's mark the proposal as submitted
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        # It cannot be evaluated: no call evaluation yet
        self.assertFalse(proposal.can_create_evaluation())
        self.assertEqual('To evaluate the proposal a Call Evaluation needs to be created',
                         proposal.reason_cannot_create_evaluation())

        call_evaluation = CallEvaluation(call=proposal.call, panel_date=datetime.now())
        call_evaluation.save()

        self.assertTrue(proposal.can_create_evaluation())

    def test_proposal_can_eligibility_be_created_or_changed(self):
        proposal = database_population.create_proposal()

        # Eligibility cannot be created or changed: ProposalStatus is not correct
        self.assertFalse(proposal.can_eligibility_be_created_or_changed())
        self.assertEqual('Proposal status needs to be submitted in order to create/edit eligibility',
                         proposal.reason_eligibility_cannot_be_created_or_changed())

        # Let's make the ProposalStatus submitted...
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        self.assertTrue(proposal.can_eligibility_be_created_or_changed())
