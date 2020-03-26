from django.test import TestCase

from project_core.forms.partners import ProposalPartnerItemForm
from project_core.tests import database_population


class PartnerFormTest(TestCase):
    def setUp(self):
        self.proposal = database_population.create_proposal()

        self.academic_title = database_population.create_academic_title()
        self.career_stage = database_population.create_career_stage()
        self.organisations = database_population.create_organisation_names()
        self.role = database_population.create_role()

    def test_save_partner(self):
        data = {'person__physical_person__orcid': '1111-0002-1825-0097',
                'person__physical_person__first_name': 'John',
                'person__physical_person__surname': 'Smith',
                'person__academic_title': str(self.academic_title.id),
                'person__group': 'Lab of Science',
                'person__career_stage': str(self.career_stage.id),
                'role': str(self.role.id),
                'role_description': 'Very useful!',
                'competences': 'Many',
                'person__organisations': self.organisations
                }

        partner_form = ProposalPartnerItemForm(data=data, call=self.proposal.call)
        self.assertTrue(partner_form.is_valid())
        partner_form.save_partner(self.proposal)
