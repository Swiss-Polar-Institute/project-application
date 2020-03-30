from datetime import datetime

from django.test import TestCase, Client
from django.urls import reverse

from ProjectApplication import settings
from evaluation.models import ProposalEvaluation, CallEvaluation
from evaluation.views import CallEvaluationValidation
from project_core.models import Proposal, ProposalStatus, Project
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
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-proposal-evaluation-add') + f'?proposal={self._proposal.id}')

        self.assertEqual(response.status_code, 200)

    def test_proposal_evaluation_detail_permission_denied(self):
        c = Client()
        response = c.get(reverse('logged-proposal-evaluation-add') + f'?proposal={self._proposal.id}')

        self.assertEqual(response.status_code, 302)


class ProposalEvaluationListTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-evaluation-list'))

        self.assertEqual(response.status_code, 200)


class CallEvaluationUpdateTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        call_evaluation = CallEvaluation()
        call_evaluation.call = self._proposal.call
        call_evaluation.panel_date = datetime.today()
        call_evaluation.save()

        response = self._client_management.get(
            reverse('logged-call-evaluation-update', kwargs={'pk': call_evaluation.id}))

        self.assertEqual(response.status_code, 200)


class ProposalListTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-call-evaluation-list-proposals', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['call'], self._proposal.call)
        self.assertEqual(response.context_data['proposals'].count(), 0)


class ProposalEvaluationDetailTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        proposal_evaluation = ProposalEvaluation()
        proposal_evaluation.proposal = self._proposal
        proposal_evaluation.save()

        response = self._client_management.get(
            reverse('logged-proposal-evaluation-detail', kwargs={'pk': proposal_evaluation.id}))

        self.assertEqual(response.status_code, 200)


class CallEvaluationDetailTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get_context_data(self):
        call_evaluation = CallEvaluation()
        call_evaluation.call = self._proposal.call
        call_evaluation.panel_date = datetime.today()
        call_evaluation.save()

        response = self._client_management.get(
            reverse('logged-call-evaluation-detail', kwargs={'pk': call_evaluation.id}))

        self.assertEqual(response.status_code, 200)


class ProposalDetailTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-call-evaluation-proposal-detail', kwargs={'pk': self._proposal.id}))

        self.assertEqual(response.status_code, 200)


class CallEvaluationSummaryTest(TestCase):
    def setUp(self):
        self._user = database_population.create_management_user()
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-call-evaluation-summary', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)


class CallEvaluationValidationTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get_context_data(self):
        call_evaluation = CallEvaluation()
        call_evaluation.call = self._proposal.call
        call_evaluation.panel_date = datetime.today()
        call_evaluation.save()

        # Checks that 1 proposal, 0 eligible...
        response = self._client_management.get(
            reverse('logged-call-evaluation-validation', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)

        context_data = response.context_data
        self.assertEqual(context_data['all_good'], False)
        self.assertEqual(context_data['can_close'], False)
        self.assertEqual(context_data['total_number_of_proposals'], 1)
        self.assertEqual(context_data['total_number_of_eligible'], 0)
        self.assertEqual(context_data['total_number_of_funded'], 0)
        self.assertEqual(context_data['total_number_of_eligible_not_funded'], 0)

        # Makes the proposal eligible
        self._proposal.eligibility = Proposal.ELIGIBLE
        self._proposal.save()

        # Checks that 1 proposal, 1 eligible, 0 funded
        response = self._client_management.get(
            reverse('logged-call-evaluation-validation', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)

        context_data = response.context_data
        self.assertEqual(context_data['all_good'], False)
        self.assertEqual(context_data['can_close'], False)
        self.assertEqual(context_data['total_number_of_proposals'], 1)
        self.assertEqual(context_data['total_number_of_eligible'], 1)
        self.assertEqual(context_data['total_number_of_funded'], 0)
        self.assertEqual(context_data['total_number_of_eligible_not_funded'], 1)

        # Funds the proposal. In reality the form would force the attached letter before it's funded, etc.
        # but here accessing to the model straight away all the rest is not needed
        proposal_evaluation = ProposalEvaluation()
        proposal_evaluation.proposal = self._proposal
        proposal_evaluation.board_decision = ProposalEvaluation.BOARD_DECISION_FUND
        proposal_evaluation.save()

        # Checks that 1 proposal, 1 eligible, 1 funded
        response = self._client_management.get(
            reverse('logged-call-evaluation-validation', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)

        context_data = response.context_data
        self.assertEqual(context_data['all_good'], False)
        self.assertEqual(context_data['can_close'], False)
        self.assertEqual(context_data['total_number_of_proposals'], 1)
        self.assertEqual(context_data['total_number_of_eligible'], 1)
        self.assertEqual(context_data['total_number_of_funded'], 1)
        self.assertEqual(context_data['total_number_of_eligible_not_funded'], 0)


class CallCloseEvaluationTest(TestCase):
    def setUp(self):
        self._client = database_population.create_management_logged_client()
        self._proposal = database_population.create_proposal()

    def test_post(self):
        call_evaluation = CallEvaluation()
        call_evaluation.call = self._proposal.call
        call_evaluation.panel_date = datetime.today()
        call_evaluation.save()

        # Makes the proposal eligible
        self._proposal.eligibility = Proposal.ELIGIBLE
        self._proposal.save()

        # Funds the proposal. In reality the form would force the attached letter before it's funded, etc.
        # but here accessing to the model straight away all the rest is not needed
        proposal_evaluation = ProposalEvaluation()
        proposal_evaluation.proposal = self._proposal
        proposal_evaluation.board_decision = ProposalEvaluation.BOARD_DECISION_FUND
        proposal_evaluation.save()

        self.assertEqual(Project.objects.all().count(), 0)

        response = self._client.post(
            reverse('logged-call-close-evaluation', kwargs={'call_id': self._proposal.call.id}))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Project.objects.all().count(), 1)

        # Verifies created project
        project = Project.objects.all()[0]

        self.assertEqual(project.title, self._proposal.title)
        self.assertEqual(project.location, self._proposal.location)
        self.assertEqual(project.start_date, self._proposal.start_date)
        self.assertEqual(project.end_date, self._proposal.end_date)
        self.assertEqual(project.principal_investigator, self._proposal.applicant)
        self.assertEqual(project.principal_investigator, self._proposal.applicant)

        self.assertEqual(project.overarching_project, self._proposal.overarching_project)
        self.assertEqual(project.allocated_budget, self._proposal.proposalevaluation.allocated_budget)
        self.assertEqual(project.status, Project.ONGOING)

        self.assertEqual(project.call, self._proposal.call)
        self.assertEqual(project.proposal, self._proposal)

        # TODO: check project.geographical_areas and project.keywords
