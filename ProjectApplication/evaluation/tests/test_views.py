from datetime import datetime

from django.test import TestCase, Client
from django.urls import reverse

from ProjectApplication import settings
from evaluation.models import ProposalEvaluation, CallEvaluation
from evaluation.views import CallEvaluationValidation
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
        check_result = CallEvaluationValidation._check_all_submitted_proposals_have_eligibility_set(proposals)
        self.assertEqual(check_result['proposals'].count(), 1)
        self.assertEqual(check_result['proposals'][0], proposal)

        # Sets it not eligible
        proposal.eligibility = Proposal.NOTELIGIBLE
        proposal.save()

        # Then all good for this test
        check_result = CallEvaluationValidation._check_all_submitted_proposals_have_eligibility_set(proposals)
        self.assertEqual(check_result['proposals'].count(), 0)

    def test_check_eligible_proposals_have_evaluation(self):
        proposal = database_population.create_proposal()

        proposal.eligibility = Proposal.ELIGIBILITYNOTCHECKED
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        proposals = Proposal.objects.filter(uuid=proposal.uuid)

        # Expects one proposal that is eligible but doesn't have a proposal evaluation
        check_result = CallEvaluationValidation._check_all_submitted_proposals_have_eligibility_set(proposals)
        self.assertEqual(check_result['proposals'].count(), 1)

        proposal_evaluation = ProposalEvaluation()
        proposal_evaluation.proposal = proposal
        proposal_evaluation.save()

        proposal.eligibility = Proposal.ELIGIBLE
        proposal.save()

        proposals = Proposal.objects.filter(uuid=proposal.uuid)

        # Now it has the proposal evaluation, it's all good
        check_result = CallEvaluationValidation._check_all_submitted_proposals_have_eligibility_set(proposals)
        self.assertEqual(check_result['proposals'].count(), 0)


class ProposalEvaluationUpdateTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._user = database_population.create_management_user()

    def test_proposal_evaluation_detail(self):
        c = Client()
        c.login(username='unittest_management', password='12345')
        response = c.get(reverse('logged-proposal-evaluation-add') + f'?proposal={self._proposal.id}')

        self.assertEqual(response.status_code, 200)

    def test_proposal_evaluation_detail_permission_denied(self):
        c = Client()
        response = c.get(reverse('logged-proposal-evaluation-add') + f'?proposal={self._proposal.id}')

        self.assertEqual(response.status_code, 302)


class ProposalEvaluationListTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()

    def test_list(self):
        c = Client()
        c.login(username='unittest_management', password='12345')
        response = c.get(reverse('logged-evaluation-list'))

        self.assertEqual(response.status_code, 200)


class CallEvaluationUpdateTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()

    def test_detail(self):
        call_evaluation = CallEvaluation()
        call_evaluation.call = self._proposal.call
        call_evaluation.panel_date = datetime.today()
        call_evaluation.save()

        c = Client()
        c.login(username='unittest_management', password='12345')
        response = c.get(reverse('logged-call-evaluation-update', kwargs={'pk': call_evaluation.id}))

        self.assertEqual(response.status_code, 200)


class ProposalListTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()

    def test_detail(self):
        c = Client()
        c.login(username='unittest_management', password='12345')
        response = c.get(reverse('logged-call-evaluation-list-proposals', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['call'], self._proposal.call)
        self.assertEqual(response.context_data['proposals'].count(), 0)


class ProposalEvaluationDetailTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()

    def test_detail(self):
        c = Client()
        c.login(username='unittest_management', password='12345')

        proposal_evaluation = ProposalEvaluation()
        proposal_evaluation.proposal = self._proposal
        proposal_evaluation.save()

        response = c.get(reverse('logged-proposal-evaluation-detail', kwargs={'pk': proposal_evaluation.id}))

        self.assertEqual(response.status_code, 200)
