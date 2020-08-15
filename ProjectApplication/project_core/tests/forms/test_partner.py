from django.test import TestCase

from project_core.forms.partners import ProposalPartnerItemForm
from project_core.models import PhysicalPerson, Role
from project_core.tests import database_population


class PartnerFormTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()

        self._academic_title = database_population.create_academic_title()
        self._career_stage = database_population.create_career_stage()
        self._organisations = database_population.create_organisation_names()
        self._role = database_population.create_roles()[0]

    def test_save_partner(self):
        data = {'person__physical_person__orcid': '1111-0002-1825-0097',
                'person__physical_person__first_name': 'John',
                'person__physical_person__surname': 'Smith',
                'person__academic_title': self._academic_title,
                'person__group': 'Lab of Science',
                'person__career_stage': self._career_stage.id,
                'role': Role.objects.get(name='Principal Investigator').id,
                'role_description': 'Very useful!',
                'competences': 'Many',
                'person__organisations': [self._organisations[0].id],
                }

        partner_form = ProposalPartnerItemForm(data, call=self._proposal.call)

        self.assertEqual(PhysicalPerson.objects.filter(orcid='1111-0002-1825-0097').count(), 0)
        self.assertEqual(self._proposal.proposalpartner_set.count(), 0)

        self.assertTrue(partner_form.is_valid())
        partner_form.save_partner(self._proposal)

        self.assertEqual(PhysicalPerson.objects.filter(orcid='1111-0002-1825-0097').count(), 1)
        self.assertEqual(self._proposal.proposalpartner_set.count(), 1)
