from django.contrib.auth.models import User, Group
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

        eligibility_decision = EligibilityDecisionForm(data=data, proposal_uuid=proposal.uuid)

        self.assertTrue(eligibility_decision.is_valid())
        eligibility_decision.save_eligibility(self._user)

        proposal.refresh_from_db()
        self.assertEqual(proposal.eligibility, Proposal.ELIGIBLE)
        self.assertEqual(proposal.eligibility_comment, comment)

    def test_not_eligible_missing_comment(self):
        proposal = create_proposal()

        self.assertEqual(proposal.eligibility, Proposal.ELIGIBILITYNOTCHECKED)

        data = {'comment': '',
                'eligible': 'False'
                }

        eligibility_decision = EligibilityDecisionForm(data=data, proposal_uuid=proposal.uuid)

        self.assertFalse(eligibility_decision.is_valid())

    def test_not_eligible(self):
        proposal = create_proposal()

        self.assertEqual(proposal.eligibility, Proposal.ELIGIBILITYNOTCHECKED)
        comment = 'Test this is part of a unit test'

        data = {'comment': comment,
                'eligible': 'False'
                }

        eligibility_decision = EligibilityDecisionForm(data=data, proposal_uuid=proposal.uuid)

        self.assertTrue(eligibility_decision.is_valid())

        eligibility_decision.save_eligibility(self._user)

        proposal.refresh_from_db()

        self.assertEqual(proposal.eligibility, Proposal.NOTELIGIBLE)
        self.assertEqual(proposal.eligibility_comment, comment)
