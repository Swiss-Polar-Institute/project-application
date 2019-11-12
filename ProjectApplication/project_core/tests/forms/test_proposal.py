from datetime import datetime

from django.test import TestCase

from project_core.forms.proposal import ProposalForm
from project_core.models import CallQuestion, Call, GeographicalArea, Keyword, ProposalStatus, PersonPosition, \
    PhysicalPerson, PersonTitle
from project_core.tests import database_population
from project_core.tests import utils


class CallFormTest(TestCase):
    def setUp(self):
        call = database_population.create_call()
        template_questions = database_population.create_template_questions()
        CallQuestion.objects.get_or_create(call=call, template_question=template_questions[0], order=10)

        database_population.create_geographical_areas()
        database_population.create_keywords()

    def test_proposal_form(self):
        data = {'title': 'Collect algae around Greenland',
                'provisional_start_date': datetime(2021, 7, 30),
                'provisional_end_date': datetime(2021, 9, 15),
                'duration_months': '3',
                'call_id': Call.objects.get(long_name='GreenLAnd Circumnavigation Expedition').id}

        data = utils.dict_to_multivalue_dict(data)
        data.setlist('geographical_areas', [GeographicalArea.objects.get(name='Antarctic').id])

        data.setlist('keywords', [Keyword.objects.get(name='Birds').id])

        proposal_form = ProposalForm(call=Call.objects.get(long_name='GreenLAnd Circumnavigation Expedition'),
                                     data=data)

        self.assertTrue(proposal_form.is_valid())

        proposal = proposal_form.save(commit=False)
        proposal.applicant = create_person_position()
        proposal.proposal_status, created = ProposalStatus.objects.get_or_create(name='Submitted')
        proposal.save()


def create_person_position():
    physical_person, created = PhysicalPerson.objects.get_or_create(first_name='John', surname='Doe')
    academic_title, created = PersonTitle.objects.get_or_create(title='Mr')
    person_position, created = PersonPosition.objects.get_or_create(person=physical_person,
                                                                    academic_title=academic_title, data_policy=True,
                                                                    contact_newsletter=True)
    return person_position
