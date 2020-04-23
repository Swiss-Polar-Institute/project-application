from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from ProjectApplication import settings
from evaluation.forms.proposal_evaluation import ProposalEvaluationForm
from evaluation.models import ProposalEvaluation, CallEvaluation
from project_core.models import ProposalStatus
from project_core.tests import database_population
from project_core.tests.database_population import create_proposal, create_reviewer


class BudgetItemFormTest(TestCase):
    def setUp(self):
        self._user = User.objects.create_user('TestUser', 'test@example.com', 'password')
        group, _ = Group.objects.get_or_create(name=settings.MANAGEMENT_GROUP_NAME)

        ProposalStatus.objects.get_or_create(name=settings.PROPOSAL_STATUS_SUBMITTED)

        group.user_set.add(self._user)
        group.save()

        self._user_no_manager = User.objects.create_user('TestUserNoManager', 'test2@example.com', 'password')

    @staticmethod
    def _create_call_evaluation(call):
        call_evaluation = CallEvaluation()
        call_evaluation.call = call
        call_evaluation.panel_date = datetime.today()
        call_evaluation.save()

    def test_save(self):
        self.assertEqual(ProposalEvaluation.objects.count(), 0)
        proposal = create_proposal()

        BudgetItemFormTest._create_call_evaluation(proposal.call)

        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        reviewers = [create_reviewer()]

        proposal.call.reviewer_set.add(*reviewers)

        data = {'proposal': proposal,
                'allocated_budget': 10_000,
                'panel_remarks': 'Very good',
                'feedback_to_applicant': 'Keep working on it!',
                'panel_recommendation': ProposalEvaluation.PANEL_RECOMMENDATION_FUND,
                'board_decision': ProposalEvaluation.BOARD_DECISION_FUND,
                'decision_date': datetime.today(),
                'reviewers': reviewers
                }

        proposal_evaluation_form = ProposalEvaluationForm(data=data, proposal=proposal)
        self.assertTrue(proposal_evaluation_form.is_valid())
        proposal_evaluation_form.save(user=self._user)

        self.assertEqual(ProposalEvaluation.objects.count(), 1)

    def test_clean_missing_file(self):
        proposal = create_proposal()
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        data = {'proposal': proposal,
                'allocated_budget': 10_000,
                'panel_remarks': 'Very good',
                'decision_letter_date': datetime.today(),
                'feedback_to_applicant': 'Keep working on it!',
                'panel_recommendation': ProposalEvaluation.PANEL_RECOMMENDATION_FUND,
                'board_decision': ProposalEvaluation.BOARD_DECISION_FUND,
                }

        proposal_evaluation_form = ProposalEvaluationForm(data=data, proposal=proposal)
        self.assertFalse(proposal_evaluation_form.is_valid())
        self.assertIn('decision_letter', proposal_evaluation_form.errors)

    def test_save_permission_denied(self):
        proposal = create_proposal()
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        data = {'proposal': proposal,
                'allocated_budget': 10_000,
                'panel_remarks': 'Very good',
                'feedback_to_applicant': 'Keep working on it!',
                'panel_recommendation': ProposalEvaluation.PANEL_RECOMMENDATION_FUND,
                'board_decision': ProposalEvaluation.BOARD_DECISION_FUND,
                }

        proposal_evaluation_form = ProposalEvaluationForm(data=data, proposal=proposal)
        self.assertRaises(PermissionDenied, proposal_evaluation_form.save, user=self._user_no_manager)

    def test_save_permission_denied_call_closed(self):
        proposal = create_proposal()
        proposal.proposal_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        proposal.save()

        reviewers = [create_reviewer()]

        proposal.call.reviewer_set.add(*reviewers)

        data = {'proposal': proposal,
                'allocated_budget': 10_000,
                'panel_remarks': 'Very good',
                'feedback_to_applicant': 'Keep working on it!',
                'panel_recommendation': ProposalEvaluation.PANEL_RECOMMENDATION_FUND,
                'board_decision': ProposalEvaluation.BOARD_DECISION_FUND,
                'decision_date': datetime.today(),
                'reviewers': reviewers
                }

        call_evaluation = CallEvaluation()
        call_evaluation.panel_date = datetime.today()
        call_evaluation.call = proposal.call
        call_evaluation.close(database_population.create_management_user())

        proposal_evaluation_form = ProposalEvaluationForm(data=data, proposal=proposal)
        self.assertTrue(proposal_evaluation_form.is_valid())

        self.assertRaises(PermissionDenied, proposal_evaluation_form.save, user=self._user)
        self.assertEqual(ProposalEvaluation.objects.count(), 0)
