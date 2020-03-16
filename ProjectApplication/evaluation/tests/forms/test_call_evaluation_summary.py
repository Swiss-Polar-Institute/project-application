from django.test import TestCase

from ProjectApplication import settings
from evaluation.models import ProposalEvaluation
from evaluation.views import CallEvaluationSummary
from project_core.models import Proposal, ProposalStatus
from project_core.tests import database_population


class CallEvaluationSummaryViewTest(TestCase):
    def setUp(self):
        pass

    def test_check_all_submitted_proposals_have_eligibility(self):
        proposal = database_population.create_proposal()

        proposal.eligibility = Proposal.ELIGIBILITYNOTCHECKED
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        proposals = Proposal.objects.filter(uuid=proposal.uuid)

        # Expects one Proposal that is submitted but eligibility not checked...
        check_result = CallEvaluationSummary._check_all_submitted_proposals_have_eligibility_set(proposals)
        self.assertEqual(check_result['proposals'].count(), 1)
        self.assertEqual(check_result['proposals'][0], proposal)

        # Sets it not eligible
        proposal.eligibility = Proposal.NOTELIGIBLE
        proposal.save()

        # Then all good for this test
        check_result = CallEvaluationSummary._check_all_submitted_proposals_have_eligibility_set(proposals)
        self.assertEqual(check_result['proposals'].count(), 0)

    def check_eligible_proposals_have_evaluation(self):
        proposal = database_population.create_proposal()

        proposal.eligibility = Proposal.ELIGIBILITYNOTCHECKED
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.eligibility = Proposal.ELIGIBLE
        proposal.save()

        proposals = Proposal.objects.filter(uuid=proposal.uuid)

        # Expects one proposal that is eligible but doesn't have a proposal evaluation
        check_result = CallEvaluationSummary._check_eligible_proposals_have_evaluation(proposals)
        self.assertEqual(check_result['proposals'].count(), 1)

        proposal_evaluation = ProposalEvaluation()
        proposal_evaluation.proposal = proposal
        proposal_evaluation.save()

        # Now it has the proposal evaluation, it's all good
        check_result = CallEvaluationSummary._check_eligible_proposals_have_evaluation(proposals)
        self.assertEqual(check_result['proposals'].count(), 0)
