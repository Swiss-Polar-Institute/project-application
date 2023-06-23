import re
from datetime import datetime, timedelta

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.timezone import utc

from project_core.models import Proposal, Country, Role
from project_core.tests import database_population
from variable_templates.tests import database_population as database_population_variable_templates

def get_response_messages(response):
    # Might e a better way, doing this for Django 3.2
    from django.contrib.messages import get_messages
    return list(get_messages(response.wsgi_request))

class ProposalFormTest(TestCase):
    def setUp(self):
        self._budget_categories = database_population.create_budget_categories()
        self._person_titles = database_population.create_person_titles()
        self._genders = database_population.create_genders()
        self._organisations = database_population.create_organisations()
        self._organisation_names = database_population.create_organisation_names()
        self._geographical_areas = database_population.create_geographical_areas()
        self._keywords = database_population.create_keywords()
        self._career_stage = database_population.create_career_stage()
        self._role = database_population.create_roles()[0]
        self._call = database_population.create_call()
        self._client_management = database_population.create_applicant_logged_client()

        database_population.create_proposal_status()
        database_population_variable_templates.create_default_template_variables()

    def _proposal_post_data(self, start_date):
        start_date_str = start_date.strftime('%d-%m-%Y')
        end_date_str = (start_date + timedelta(days=10)).strftime('%d-%m-%Y')

        orcid = '0000-1111-2222-3333'

        return MultiValueDict(
            {
                'person_form-academic_title': [self._person_titles[0].id], 'person_form-first_name': ['John'],
                'person_form-surname': ['Doe'],
                'person_form-orcid': [orcid],
                'person_form-gender': [self._genders[0].id],
                'person_form-email': ['test@example.com'],
                'person_form-phone': ['+41 22 222 33 33'],
                'person_form-organisation_names': [self._organisation_names[0].id],
                'person_form-group': ['A new group'],
                'person_form-career_stage': [self._career_stage.id],
                'proposal_form-call_id': [self._call.id],
                'proposal_form-title': ['Replace this title!'],
                'proposal_form-geographical_areas': [self._geographical_areas[0].id],
                'proposal_form-keywords': [[str(keyword.id) for keyword in self._keywords]],
                'proposal_form-start_date': [start_date_str],
                'proposal_form-end_date': [end_date_str],
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
                'budget_form-TOTAL_FORMS': ['1'], 'budget_form-INITIAL_FORMS': ['1'],
                'budget_form-MIN_NUM_FORMS': ['1'],
                'budget_form-MAX_NUM_FORMS': ['1000'], 'budget_form-0-id': [''], 'budget_form-1-id': [''],
                'budget_form-2-id': [''], 'budget_form-3-id': [''], 'budget_form-4-id': [''], 'budget_form-5-id': [''],
                'budget_form-6-id': [''], 'budget_form-7-id': [''],
                'budget_form-0-category': [self._budget_categories[0].id],
                'budget_form-0-details': ['DNA sampling'], 'budget_form-0-amount': ['10000'],
                'funding_form-TOTAL_FORMS': ['1'],
                'funding_form-INITIAL_FORMS': ['0'], 'funding_form-MIN_NUM_FORMS': ['0'],
                'funding_form-MAX_NUM_FORMS': ['1000'], 'funding_form-__prefix__-organisation': [''],
                'funding_form-__prefix__-funding_status': [''], 'funding_form-__prefix__-amount': [''],
                'funding_form-__prefix__-proposal': [''], 'funding_form-__prefix__-id': [''],
                'funding_form-__prefix__-DELETE': [''], 'funding_form-0-organisation': ['25'],
                'funding_form-0-funding_status': ['1'], 'funding_form-0-amount': ['5000'],
                'funding_form-0-proposal': [''],
                'funding_form-0-id': [''], 'funding_form-0-DELETE': [''], 'data_collection_form-privacy_policy': ['on'],
                'data_collection_form-contact_newsletter': ['on'], 'submit': ['Submit'],
                'postal_address_form-address': ['5th Avenue, 87'],
                'postal_address_form-city': ['New York'],
                'postal_address_form-postcode': ['429ZKDKZMM'],
                'postal_address_form-country': [Country.objects.get(name='Switzerland').id],

                'applicant_role_description_form-role': [Role.objects.get(name='Principal Investigator').id],
                'applicant_role_description_form-description': ['Very important role!'],
                'applicant_role_description_form-competences': ['Very important competences'],
            }
        )

    def test_proposal_get(self):

        self._call.proposal_partner_question = True
        self._call.save()

        response = self._client_management.get(reverse('proposal-add') + '?call={}'.format(self._call.id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Call name:')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
        self.assertContains(response, 'Roles and competences')
        self.assertContains(response, 'Partners')

    def test_proposal_no_partners_get(self):
        self._call.proposal_partner_question = False
        self._call.save()

        response = self._client_management.get(reverse('proposal-add') + '?call={}'.format(self._call.id))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Call name:')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
        self.assertNotContains(response, 'Proposal partners')

    def test_proposal_new_post(self):
        self._call.proposal_partner_question = False
        self._call.save()

        data = self._proposal_post_data(self._call.submission_deadline + timedelta(days=1))
        data['proposal_form-title'] = ['Collect algae']

        response = self._client_management.post(f'{reverse("proposal-add")}?call={self._call.id}', data=data)
        self.assertEqual(response.status_code, 302)
        reg_exp = '/proposal/thank-you/([0-9a-z-]+)/'
        self.assertRegex(response.url, reg_exp)
        m = re.search(reg_exp, response.url)
        uuid = m.group(1)

        proposal = Proposal.objects.get(uuid=uuid)
        self.assertEqual(proposal.title, 'Collect algae')

        self._call.proposal_partner_question = True
        self._call.save()

    def test_proposal_new_post_too_late(self):
        self._call.submission_deadline = utc.localize(datetime(2000, 1, 1))
        self._call.save()

        data = self._proposal_post_data(self._call.submission_deadline + timedelta(days=1))
        data['proposal_form-title'] = ['Too late?']

        response = self._client_management.post(f'{reverse("proposal-add")}?call={self._call.id}', data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/applicant/proposal/cannot-modify/', response.url)

        messages = get_response_messages(response)

        self.assertIn('deadline has now passed', messages[0].message)

    def test_only_one_partner(self):
        data = self._proposal_post_data(self._call.submission_deadline + timedelta(days=1))
        data['proposal_form-title'] = ['Collect algae again']

        data.update(MultiValueDict({'proposal_partners_form-0-person__physical_person__orcid': ['0000-0001-8672-0508'],
                                    'proposal_partners_form-0-person__academic_title': [self._person_titles[0].id],
                                    'proposal_partners_form-0-person__physical_person__first_name': ['John'],
                                    'proposal_partners_form-0-person__physical_person__surname': ['Doe'],
                                    'proposal_partners_form-0-person__group': ['Some group'],
                                    'proposal_partners_form-0-person__career_stage': [self._career_stage.id],
                                    'proposal_partners_form-0-person__organisations': [self._organisation_names[0].id],
                                    'proposal_partners_form-0-role': [Role.objects.get(name='Collaborator').id],
                                    'proposal_partners_form-0-role_description': ['Will help loads'],
                                    'proposal_partners_form-0-competences': ['Many'],
                                    'proposal_partners_form-0-DELETE': [''],

                                    }))

        response = self._client_management.post(f'{reverse("proposal-add")}?call={self._call.id}', data=data)
        self.assertEqual(response.status_code, 302)

        proposal = Proposal.objects.get(title='Collect algae again')
        self.assertEqual(proposal.proposalpartner_set.count(), 1)
        self.assertEqual(proposal.proposalpartner_set.all()[0].person.person.first_name, 'John')

    def test_only_two_partners_duplicated(self):
        data = self._proposal_post_data(self._call.submission_deadline + timedelta(days=1))
        data['proposal_form-title'] = ['Collect algae again']

        data.update(MultiValueDict({'proposal_partners_form-0-person__physical_person__orcid': ['0000-0001-8672-0508'],
                                    'proposal_partners_form-0-person__academic_title': [self._person_titles[0].id],
                                    'proposal_partners_form-0-person__physical_person__first_name': ['John'],
                                    'proposal_partners_form-0-person__physical_person__surname': ['Doe'],
                                    'proposal_partners_form-0-person__group': ['Some group'],
                                    'proposal_partners_form-0-person__career_stage': [self._career_stage.id],
                                    'proposal_partners_form-0-person__organisations': [self._organisation_names[0].id],
                                    'proposal_partners_form-0-role': [Role.objects.get(name='Principal Investigator').id],
                                    'proposal_partners_form-0-role_description': ['Will help loads'],
                                    'proposal_partners_form-0-competences': ['Many'],
                                    'proposal_partners_form-0-DELETE': [''],

                                    'proposal_partners_form-1-person__physical_person__orcid': ['0000-0001-8672-0508'],
                                    'proposal_partners_form-1-person__academic_title': [self._person_titles[0].id],
                                    'proposal_partners_form-1-person__physical_person__first_name': ['John'],
                                    'proposal_partners_form-1-person__physical_person__surname': ['Doe'],
                                    'proposal_partners_form-1-person__group': ['Some group'],
                                    'proposal_partners_form-1-person__career_stage': [self._career_stage.id],
                                    'proposal_partners_form-1-person__organisations': [self._organisation_names[0].id],
                                    'proposal_partners_form-1-role': [Role.objects.get(name='Collaborator').id],
                                    'proposal_partners_form-1-role_description': ['Will help loads'],
                                    'proposal_partners_form-1-competences': ['Many'],
                                    'proposal_partners_form-1-DELETE': [''],
                                    'proposal_partners_form-TOTAL_FORMS': ['2'],

                                    }))

        response = self._client_management.post(f'{reverse("proposal-add")}?call={self._call.id}', data=data)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Call name:')
        self.assertContains(response, 'GreenLAnd Circumnavigation Expedition')
        self.assertContains(response,
                            'A proposal partner has been entered more than once. Use the remove button to delete the duplicated partner.')

        self.assertEqual(Proposal.objects.all().count(), 0)

    def test_only_two_partners_duplicated_deleted(self):
        data = self._proposal_post_data(self._call.submission_deadline + timedelta(days=1))
        data['proposal_form-title'] = ['Collect algae again']

        data.update(MultiValueDict({'proposal_partners_form-0-person__physical_person__orcid': ['0000-0001-8672-0508'],
                                    'proposal_partners_form-0-person__academic_title': [self._person_titles[0].id],
                                    'proposal_partners_form-0-person__physical_person__first_name': ['John'],
                                    'proposal_partners_form-0-person__physical_person__surname': ['Doe'],
                                    'proposal_partners_form-0-person__group': ['Some group'],
                                    'proposal_partners_form-0-person__career_stage': [self._career_stage.id],
                                    'proposal_partners_form-0-person__organisations': [self._organisation_names[0].id],
                                    'proposal_partners_form-0-role': [Role.objects.get(name='Collaborator').id],
                                    'proposal_partners_form-0-role_description': ['Will help loads'],
                                    'proposal_partners_form-0-competences': ['Many'],
                                    'proposal_partners_form-0-DELETE': [''],

                                    'proposal_partners_form-1-person__physical_person__orcid': ['0000-0001-8672-0508'],
                                    'proposal_partners_form-1-person__academic_title': [self._person_titles[0].id],
                                    'proposal_partners_form-1-person__physical_person__first_name': ['John'],
                                    'proposal_partners_form-1-person__physical_person__surname': ['Doe'],
                                    'proposal_partners_form-1-person__group': ['Some group'],
                                    'proposal_partners_form-1-person__career_stage': [self._career_stage.id],
                                    'proposal_partners_form-1-person__organisations': [self._organisation_names[0].id],
                                    'proposal_partners_form-1-role': [Role.objects.get(name='Collaborator').id],
                                    'proposal_partners_form-1-role_description': ['Will help loads'],
                                    'proposal_partners_form-1-competences': ['Many'],
                                    'proposal_partners_form-1-DELETE': ['on'],

                                    'proposal_partners_form-TOTAL_FORMS': ['2'],
                                    }))

        response = self._client_management.post(f'{reverse("proposal-add")}?call={self._call.id}', data=data)
        self.assertEqual(response.status_code, 302)

        proposal = Proposal.objects.get(title='Collect algae again')
        self.assertEqual(proposal.proposalpartner_set.count(), 1)
        self.assertEqual(proposal.proposalpartner_set.all()[0].person.person.first_name, 'John')
