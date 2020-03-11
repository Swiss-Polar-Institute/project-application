from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from ProjectApplication import settings
from evaluation.forms.proposal_evaluation import ProposalEvaluationForm
from evaluation.models import ProposalEvaluation
from project_core.models import ProposalStatus
from project_core.tests.database_population import create_proposal


class BudgetItemFormTest(TestCase):
    def setUp(self):
        self._user = User.objects.create_user('TestUser', 'test@example.com', 'password')
        group, _ = Group.objects.get_or_create(name=settings.MANAGEMENT_GROUP_NAME)

        ProposalStatus.objects.get_or_create(name=settings.PROPOSAL_STATUS_ACCEPTED)

        group.user_set.add(self._user)
        group.save()

        ####
        self._user_no_manager = User.objects.create_user('TestUserNoManager', 'test2@example.com', 'password')

    def test_save(self):
        self.assertEqual(ProposalEvaluation.objects.count(), 0)
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
