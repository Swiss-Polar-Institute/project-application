from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from ProjectApplication import settings
from evaluation.forms.eligibility import EligibilityDecisionForm
from project_core.models import Proposal
from project_core.tests.database_population import create_proposal


class BudgetItemFormTest(TestCase):
    def setUp(self):
        self._user = User.objects.create_user('TestUser', 'test@example.com', 'password')
        group, _ = Group.objects.get_or_create(name=settings.MANAGEMENT_GROUP_NAME)

        group.user_set.add(self._user)
        group.save()

    def test_eligibility(self):
        proposal = create_proposal()

        self.assertEqual(proposal.eligibility, Proposal.ELIGIBILITYNOTCHECKED)

        comment = 'This is a test'

        data = {'comment': comment,
                'eligible': 'True'
                }

        eligibility_decision_form = EligibilityDecisionForm(data=data, proposal_id=proposal.id)

        self.assertTrue(eligibility_decision_form.is_valid())
        eligibility_decision_form.save_eligibility(self._user)

        proposal.refresh_from_db()
        self.assertEqual(proposal.eligibility, Proposal.ELIGIBLE)
        self.assertEqual(proposal.eligibility_comment, comment)

    def test_permission_denied(self):
        user_not_in_management = User.objects.create_user('TestUserNotInManagement',
                                                          'test_not_in_management@example.com', 'password')
        proposal = create_proposal()
        comment = 'This is a test'

        data = {'comment': comment,
                'eligible': 'True'
                }

        eligibility_decision_form = EligibilityDecisionForm(data=data, proposal_id=proposal.id)

        self.assertTrue(eligibility_decision_form.is_valid())

        self.assertRaises(PermissionDenied, eligibility_decision_form.save_eligibility, user_not_in_management)

    def test_not_eligible_missing_comment(self):
        proposal = create_proposal()

        self.assertEqual(proposal.eligibility, Proposal.ELIGIBILITYNOTCHECKED)

        data = {'comment': '',
                'eligible': 'False'
                }

        eligibility_decision_form = EligibilityDecisionForm(data=data, proposal_id=proposal.id)

        self.assertFalse(eligibility_decision_form.is_valid())

    def test_not_eligible(self):
        proposal = create_proposal()

        self.assertEqual(proposal.eligibility, Proposal.ELIGIBILITYNOTCHECKED)
        comment = 'Test this is part of a unit test'

        data = {'comment': comment,
                'eligible': 'False'
                }

        eligibility_decision_form = EligibilityDecisionForm(data=data, proposal_id=proposal.id)

        self.assertTrue(eligibility_decision_form.is_valid())

        eligibility_decision_form.save_eligibility(self._user)

        proposal.refresh_from_db()

        self.assertEqual(proposal.eligibility, Proposal.NOTELIGIBLE)
        self.assertEqual(proposal.eligibility_comment, comment)
