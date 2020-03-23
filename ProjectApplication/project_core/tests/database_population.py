from datetime import datetime

from django.contrib.auth.models import User, Group
from django.utils.timezone import utc

from ProjectApplication import settings
from evaluation.models import Reviewer
from project_core.models import BudgetCategory, Call, TemplateQuestion, GeographicalArea, Keyword, KeywordUid, Source, \
    PersonTitle, Gender, Organisation, Country, OrganisationUid, ProposalStatus, CareerStage, OrganisationName, \
    Proposal, PersonPosition, PhysicalPerson, FundingInstrument


def create_call(funding_instrument=None):
    call, created = Call.objects.get_or_create(long_name='GreenLAnd Circumnavigation Expedition',
                                               call_open_date=datetime(2019, 1, 1),
                                               submission_deadline=utc.localize(datetime(2025, 1, 31)),
                                               budget_maximum=100_000, other_funding_question=False,
                                               proposal_partner_question=True,
                                               funding_instrument=funding_instrument)

    return call


def create_funding_instrument():
    funding_instrument, created = FundingInstrument.objects.get_or_create(long_name='Big Expeditions')

    return funding_instrument


def create_geographical_areas():
    antarctic, created = GeographicalArea.objects.get_or_create(name='Antarctic', definition='Very south')
    arctic, created = GeographicalArea.objects.get_or_create(name='Arctic', definition='Very north')
    high_peak, created = GeographicalArea.objects.get_or_create(name='High peaks', definition='Very high')

    return antarctic, arctic, high_peak


def create_keywords():
    source, created = Source.objects.get_or_create(source='Unit test')

    keyword_uuid, created = KeywordUid.objects.get_or_create(uid='test-2040242', source=source)

    algae, created = Keyword.objects.get_or_create(name='Algae', uid=keyword_uuid)
    birds, created = Keyword.objects.get_or_create(name='Birds', uid=keyword_uuid)
    penguins, created = Keyword.objects.get_or_create(name='Penguins', uid=keyword_uuid)
    ice, created = Keyword.objects.get_or_create(name='Ice', uid=keyword_uuid)
    micro_plastics, created = Keyword.objects.get_or_create(name='Micro-plastics', uid=keyword_uuid)

    source, created = Source.objects.get_or_create(source='External User')

    keyword_uuid, created = KeywordUid.objects.get_or_create(uid='de20ndwneip', source=source)

    cloud, created = Keyword.objects.get_or_create(name='Cloud', uid=keyword_uuid)
    rain, created = Keyword.objects.get_or_create(name='Rain', uid=keyword_uuid)
    snow, created = Keyword.objects.get_or_create(name='Snow', uid=keyword_uuid)

    return algae, birds, penguins, ice, micro_plastics, cloud, rain, snow


def create_career_stages():
    career, created = CareerStage.objects.get_or_create(name='PhD More than 5 years')

    return career,


def create_proposal_status():
    proposal_status_submitted, created = ProposalStatus.objects.get_or_create(name='Submitted')
    proposal_status_draft, created = ProposalStatus.objects.get_or_create(name='Draft')

    return proposal_status_submitted, proposal_status_draft


def create_budget_categories():
    travel, created = BudgetCategory.objects.get_or_create(name='Travel',
                                                           defaults={
                                                               'description': 'Funds needed to reach the destination'})

    data_processing, created = BudgetCategory.objects.get_or_create(name='Data processing',
                                                                    defaults={
                                                                        'description': 'Funds needed to process data'})

    equipment_consumables, created = BudgetCategory.objects.get_or_create(name='Equipment / consumables', defaults={
        'description': 'Budget required for equipment or other consumables that would be needed for the proposed work'})

    return travel, data_processing, equipment_consumables


def create_template_questions():
    template_question1, created = TemplateQuestion.objects.get_or_create(
        question_text='Explain which methods of transport are needed to go to the location',
        question_description='Explain it detailed',
        answer_type=TemplateQuestion.TEXT,
        answer_max_length=500)

    template_question2, created = TemplateQuestion.objects.get_or_create(
        question_text='Explain how to do science',
        question_description='In very short',
        answer_type=TemplateQuestion.TEXT,
        answer_max_length=50)

    return template_question1, template_question2


def create_management_user():
    user = User.objects.create_user(username='unittest_management', password='12345')
    group, _ = Group.objects.get_or_create(name=settings.MANAGEMENT_GROUP_NAME)

    group.user_set.add(user)
    group.save()

    return user


def create_reviewer_user():
    user = User.objects.create_user(username='unittest_reviewer', password='12345')
    group, _ = Group.objects.get_or_create(name=settings.REVIEWER_GROUP_NAME)

    group.user_set.add(user)
    group.save()

    return user


def create_reviewer():
    reviewer_user = create_reviewer_user()
    physical_person, _ = PhysicalPerson.objects.get_or_create(first_name='Alan',
                                                              surname='Smithee',
                                                              orcid='1111-0002-1825-0097'
                                                              )

    reviewer, _ = Reviewer.objects.get_or_create(user=reviewer_user, person=physical_person)
    return reviewer


def create_person_titles():
    person_title_mr, created = PersonTitle.objects.get_or_create(title='Mr')

    return person_title_mr,


def create_genders():
    gender, created = Gender.objects.get_or_create(name='Man')

    return gender,


def create_organisations():
    country, created = Country.objects.get_or_create(name='Switzerland')
    source, created = Source.objects.get_or_create(source='Somewhere in the brain')

    organisation1_uid, created = OrganisationUid.objects.get_or_create(source=source,
                                                                       uid='646a6e1c-2378-46d9-af42-a3710c5aee89')
    organisation1, created = Organisation.objects.get_or_create(long_name='École Polytechnique Fédérale de Lausanne',
                                                                short_name='EPFL', country=country,
                                                                uid=organisation1_uid)

    organisation2_uid, created = OrganisationUid.objects.get_or_create(source=source,
                                                                       uid='646a6e1c-2378-46d9-af42-a3710c5aee89')
    organisation2, created = Organisation.objects.get_or_create(long_name='Swiss Polar Foundation',
                                                                short_name='SPF', country=country,
                                                                uid=organisation2_uid)

    return organisation1, organisation2


def create_organisation_names():
    organisation1, created = OrganisationName.objects.get_or_create(name='EPFL')
    organisation2, created = OrganisationName.objects.get_or_create(name='SPF')

    return organisation1, organisation2


def create_physical_person():
    physical_person, _ = PhysicalPerson.objects.get_or_create(first_name='John',
                                                              surname='Smith',
                                                              orcid='0000-0002-1825-0097'
                                                              )

    return physical_person


def create_academic_title():
    academic_title, _ = PersonTitle.objects.get_or_create(title='Mr')
    return academic_title


def create_person_position():
    physical_person = create_physical_person()
    academic_title = create_academic_title()

    person_position, _ = PersonPosition.objects.get_or_create(person=physical_person,
                                                              academic_title=academic_title)

    return person_position


def create_proposal():
    applicant = create_person_position()
    call = create_call()

    proposal_status_draft = create_proposal_status()[1]

    proposal, _ = Proposal.objects.get_or_create(title='A test proposal',
                                                 start_date='2010-12-10',
                                                 end_date='2011-11-11',
                                                 duration_months=2,
                                                 applicant=applicant,
                                                 proposal_status=proposal_status_draft,
                                                 eligibility=Proposal.ELIGIBILITYNOTCHECKED,
                                                 call=call,
                                                 )
    keywords = create_keywords()

    proposal.keywords.add(keywords[2])
    proposal.save()

    return proposal
