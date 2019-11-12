import re

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from project_core.models import Call, BudgetCategory, PersonTitle, Gender, Organisation, GeographicalArea, Keyword, \
    Proposal
from project_core.tests import database_population


class ProposalFormTest(TestCase):
    def setUp(self):
        database_population.create_call()
        database_population.create_budget_categories()
        database_population.create_person_title()
        database_population.create_gender()
        database_population.create_organisation()
        database_population.create_geographical_areas()
        database_population.create_keywords()
        database_population.create_proposal_status()

    def test_proposal_get(self):
        c = Client()

        call = Call.objects.get(long_name='GreenLAnd Circumnavigation Expedition')
        call.proposal_partner_question = True
        call.save()

        response = c.get(reverse('proposal-add') + '?call={}'.format(call.id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Call name:')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
        self.assertContains(response, 'Proposal partners')

    def test_proposal_no_partners_get(self):
        c = Client()

        call = Call.objects.get(long_name='GreenLAnd Circumnavigation Expedition')
        call.proposal_partner_question = False
        call.save()

        response = c.get(reverse('proposal-add') + '?call={}'.format(call.id))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Call name:')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
        self.assertNotContains(response, 'Proposal partners')

    def test_proposal_new_post(self):
        c = Client()

        call = Call.objects.get(long_name='GreenLAnd Circumnavigation Expedition')
        call.proposal_partner_question = False
        call.save()

        data = MultiValueDict({
            'person_form-academic_title': [PersonTitle.objects.get(title='Mr').id], 'person_form-first_name': ['John'],
            'person_form-surname': ['Doe'],
            'person_form-gender': [Gender.objects.get(name='Man').id], 'person_form-email': ['test@example.com'],
            'person_form-organisations': [Organisation.objects.get(short_name='EPFL').id],
            'person_form-group': ['A new group'], 'proposal_form-call_id': [call.id],
            'proposal_form-title': ['Collect algae'],
            'proposal_form-geographical_areas': [GeographicalArea.objects.get(name='Antarctic').id],
            'proposal_form-keywords': [Keyword.objects.get(name='Birds').id],
            'proposal_form-provisional_start_date': ['2019-11-12'],
            'proposal_form-provisional_end_date': ['2019-11-13'],
            'proposal_form-duration_months': ['1'], 'questions_form-question_1': ['Cool'],
            'questions_form-question_2': ['Cold'], 'questions_form-question_3': ['Interesting'],
            'questions_form-question_4': ['Eye opening'], 'questions_form-question_5': ['Many'],
            'questions_form-question_6': ['Second time there!'], 'proposal_partners_form-TOTAL_FORMS': ['1'],
            'proposal_partners_form-INITIAL_FORMS': ['0'], 'proposal_partners_form-MIN_NUM_FORMS': ['0'],
            'proposal_partners_form-MAX_NUM_FORMS': ['1000'], 'proposal_partners_form-0-id': [''],
            'proposal_partners_form-0-person__academic_title': [''],
            'proposal_partners_form-0-person__physical_person__first_name': [''],
            'proposal_partners_form-0-person__physical_person__surname': [''],
            'proposal_partners_form-0-person__group': [''], 'proposal_partners_form-0-career_stage': [''],
            'proposal_partners_form-0-role': [''], 'proposal_partners_form-0-role_description': [''],
            'proposal_partners_form-0-competences': [''], 'proposal_partners_form-0-DELETE': [''],
            'budget_form-TOTAL_FORMS': ['1'], 'budget_form-INITIAL_FORMS': ['1'], 'budget_form-MIN_NUM_FORMS': ['1'],
            'budget_form-MAX_NUM_FORMS': ['1000'], 'budget_form-0-id': [''], 'budget_form-1-id': [''],
            'budget_form-2-id': [''], 'budget_form-3-id': [''], 'budget_form-4-id': [''], 'budget_form-5-id': [''],
            'budget_form-6-id': [''], 'budget_form-7-id': [''],
            'budget_form-0-category': [BudgetCategory.objects.get(name='Travel').id],
            'budget_form-0-details': ['DNA sampling'], 'budget_form-0-amount': ['10000'],
            'funding_form-TOTAL_FORMS': ['1'],
            'funding_form-INITIAL_FORMS': ['0'], 'funding_form-MIN_NUM_FORMS': ['0'],
            'funding_form-MAX_NUM_FORMS': ['1000'], 'funding_form-__prefix__-organisation': [''],
            'funding_form-__prefix__-funding_status': [''], 'funding_form-__prefix__-amount': [''],
            'funding_form-__prefix__-proposal': [''], 'funding_form-__prefix__-id': [''],
            'funding_form-__prefix__-DELETE': [''], 'funding_form-0-organisation': ['25'],
            'funding_form-0-funding_status': ['1'], 'funding_form-0-amount': ['5000'], 'funding_form-0-proposal': [''],
            'funding_form-0-id': [''], 'funding_form-0-DELETE': [''], 'data_collection_form-data_policy': ['on'],
            'data_collection_form-contact_newsletter': ['on'], 'submit': ['Submit']})

        response = c.post(reverse('proposal-add'), data=data)
        self.assertEqual(response.status_code, 302)
        reg_exp = '/proposal/thank-you/([0-9a-z-]+)/\?action=created'
        self.assertRegex(response.url, reg_exp)
        m = re.search(reg_exp, response.url)
        uuid = m.group(1)

        proposal = Proposal.objects.get(uuid=uuid)
        self.assertEqual(proposal.title, 'Collect algae')
