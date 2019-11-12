from datetime import datetime
from django.contrib.auth.models import User

from project_core.models import BudgetCategory, Call, TemplateQuestion, GeographicalArea, Keyword, KeywordUid, Source


def create_call():
    call, created = Call.objects.get_or_create(long_name='GreenLAnd Circumnavigation Expedition',
                                               call_open_date=datetime(2019, 1, 1),
                                               submission_deadline=datetime(2025, 1, 31),
                                               budget_maximum=100_000, other_funding_question=False,
                                               proposal_partner_question=True)

    return call


def create_geographical_areas():
    GeographicalArea.objects.get_or_create(name='Antarctic', definition='Very south')
    GeographicalArea.objects.get_or_create(name='Arctic', definition='Very north')
    GeographicalArea.objects.get_or_create(name='High peaks', definition='Very high')


def create_keywords():
    source, created = Source.objects.get_or_create(source='Unit test')

    keyword_uuid, created = KeywordUid.objects.get_or_create(uid='test-2040242', source=source)

    Keyword.objects.get_or_create(name='Algae', uid=keyword_uuid)
    Keyword.objects.get_or_create(name='Birds', uid=keyword_uuid)


def create_budget_categories():
    BudgetCategory.objects.get_or_create(name='Travel',
                                         defaults={'description': 'Funds needed to reach the destination'})

    BudgetCategory.objects.get_or_create(name='Data processing',
                                         defaults={'description': 'Funds needed to process data'})

    BudgetCategory.objects.get_or_create(name='Equipment / consumables', defaults={
        'description': 'Budget required for equipment or other consumables that would be needed for the proposed work'})


def create_template_questions():
    template_question, created = TemplateQuestion.objects.get_or_create(
        question_text='Explain which methods of transport are needed to go to the location',
        question_description='Explain it detailed',
        answer_type=TemplateQuestion.TEXT,
        answer_max_length=500)

    return [template_question]


def create_management_user():
    user = User.objects.create_user(username='unittest', password='12345')
    user.save()

    return user