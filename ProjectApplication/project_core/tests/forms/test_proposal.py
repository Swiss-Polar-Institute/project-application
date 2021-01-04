from datetime import timedelta

from django.test import TestCase

from project_core.forms.proposal import ProposalForm
from project_core.models import CallQuestion, PersonPosition, PhysicalPerson, PersonTitle, CareerStage, CallPart
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class CallFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        call_part, created = CallPart.objects.get_or_create(call=self._call,
                                                            order=1,
                                                            title='Weather',
                                                            introductory_text='Weather related questions')
        template_questions = database_population.create_template_questions()
        CallQuestion.objects.get_or_create(call_part=call_part, template_question=template_questions[0], order=10)

        self._geographical_areas = database_population.create_geographical_areas()
        self._keywords = database_population.create_keywords()
        self._proposal_status_submitted = database_population.create_proposal_status()[0]

    def test_proposal_form(self):
        data = {'title': 'Collect algae around Greenland',
                'start_date': self._call.submission_deadline + timedelta(days=10),
                'end_date': self._call.submission_deadline + timedelta(days=20),
                'duration_months': '3',
                'call_id': self._call.id}

        data = dict_to_multivalue_dict(data)
        data.setlist('geographical_areas', [self._geographical_areas[0]])

        data.setlist('keywords', self._keywords)

        proposal_form = ProposalForm(call=self._call,
                                     data=data)

        self.assertTrue(proposal_form.is_valid())

        proposal = proposal_form.save(commit=False)
        proposal.applicant = create_person_position()
        proposal.proposal_status = self._proposal_status_submitted
        proposal.save()


def create_person_position():
    physical_person, created = PhysicalPerson.objects.get_or_create(first_name='John', surname='Doe')
    academic_title, created = PersonTitle.objects.get_or_create(title='Mr')
    career_stage, created = CareerStage.objects.get_or_create(name='Post PhD')
    person_position, created = PersonPosition.objects.get_or_create(person=physical_person,
                                                                    academic_title=academic_title, privacy_policy=True,
                                                                    contact_newsletter=True,
                                                                    career_stage=career_stage)
    return person_position
