from django.contrib import admin
import project_core.models
from typing import List

# Register your models here.


class StepTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['name', 'description',]


class StepAdmin(admin.ModelAdmin):
    list_display = ('call', 'step', 'date',)
    ordering = ['call', 'step', 'date',]


class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['name',]


class CallAdmin(admin.ModelAdmin):
    list_display = ('long_name', 'short_name', 'description', 'introductory_message', 'call_open_date', 'submission_deadline', 'budget_categories_list', 'budget_maximum', 'call_questions_list')
    ordering = ['long_name', 'short_name', 'call_open_date', 'submission_deadline', 'budget_maximum',]

    def budget_categories_list(self, obj):
        budget_categories = obj.budget_categories.all()

        return ", ".join([budget_category.name for budget_category in budget_categories])

    filter_vertical = ('budget_categories', )

    def call_questions_list(self, obj):
        call_questions = obj.callquestion_set.all()

        questions = ''
        for call_question in call_questions:
            questions += call_question.question_text

        return questions


class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['description',]


class ProposalStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['description',]


class PersonTitleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ['title',]


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ['name',]


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('long_name', 'short_name', 'street', 'city', 'postal_code', 'country',)
    ordering = ['long_name', 'short_name', 'city', 'country',]


class PersonAdmin(admin.ModelAdmin):
    list_display = ('academic_title', 'first_name', 'surname', 'organisations_list', 'group',)
    ordering = ['academic_title', 'first_name', 'surname',]

    def organisations_list(self, obj):
        organisations = obj.organisations.all()

        return ', '.join([str(organisation) for organisation in organisations])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'work_telephone', 'mobile', 'person',)
    ordering = ['email_address', 'work_telephone', 'mobile', 'person',]


class GeographicalAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'definition',)
    ordering = ['name',]


class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'keywords_list', 'geographical_area_list', 'location', 'start_timeframe', 'duration', 'applicant', 'proposal_status', 'qas_list', 'call', 'date_started', 'last_modified')
    ordering = ['title', 'start_timeframe', 'duration', 'applicant', 'proposal_status', 'call', 'date_started', 'last_modified',]

    def keywords_list(self, obj):
        keywords = obj.keywords.all()

        return ", ".join([keyword.name for keyword in keywords])

    def geographical_area_list(self, obj):
        geographical_areas = obj.geographical_areas.all()

        return ", ".join([geographical_area.area for geographical_area in geographical_areas])

    def qas_list(self, obj):
        qas = obj.proposalqatext_set.all()

        result = ''
        for qa in qas:
            qa: project_core.models.ProposalQAText

            result += 'Q: {}, A: {}'.format(qa.call_question.question_text, qa.answer)

        return result


class ProposedBudgetItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'details', 'amount', 'proposal', )
    ordering = ['details', 'amount', 'proposal', ]
    search_fields = ('category__name', 'details', 'amount', 'proposal__title', )


class FundingStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'description', )
    ordering = ['status', ]


class ProposalFundingItemAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'organisation', 'status', 'amount')
    ordering = ['proposal', 'organisation', 'status', 'amount']


class CallQuestionAdmin(admin.ModelAdmin):
    list_display = ('call', 'question_text', 'question_description', 'answer_type', 'answer_max_length', 'time_added', 'order')
    ordering = ['call', 'question_text', 'answer_type', 'answer_max_length', 'time_added', 'order',]


class TemplateQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_description', 'answer_type', 'answer_max_length')
    ordering = ['question_text', 'answer_type', 'answer_max_length']


class ProposalQATextAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'call_question', 'answer',)
    ordering = ['proposal', 'call_question',]


class CareerStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ['name']


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type')
    ordering = ['name', 'type']


class ProposalPartnerAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'person', 'career_stage', 'role', 'role_description', 'competences')
    ordering = ['proposal', 'person', 'career_stage', 'role']


class ProposalCommentAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'text', 'user', 'time')
    ordering = ['proposal', 'text', 'user', 'time']


class CallCommentAdmin(admin.ModelAdmin):
    list_display = ('call', 'text', 'user', 'time')
    ordering = ['call', 'text', 'user', 'time']


admin.site.register(project_core.models.StepType, StepTypeAdmin)
admin.site.register(project_core.models.Step, StepAdmin)
admin.site.register(project_core.models.BudgetCategory, BudgetCategoryAdmin)
admin.site.register(project_core.models.Call, CallAdmin)
admin.site.register(project_core.models.Keyword, KeywordAdmin)
admin.site.register(project_core.models.ProposalStatus, ProposalStatusAdmin)
admin.site.register(project_core.models.PersonTitle, PersonTitleAdmin)
admin.site.register(project_core.models.Country, CountryAdmin)
admin.site.register(project_core.models.Organisation, OrganisationAdmin)
admin.site.register(project_core.models.Person, PersonAdmin)
admin.site.register(project_core.models.Contact, ContactAdmin)
admin.site.register(project_core.models.GeographicalArea, GeographicalAreaAdmin)
admin.site.register(project_core.models.Proposal, ProposalAdmin)
admin.site.register(project_core.models.ProposedBudgetItem, ProposedBudgetItemAdmin)
admin.site.register(project_core.models.FundingStatus, FundingStatusAdmin)
admin.site.register(project_core.models.ProposalFundingItem, ProposalFundingItemAdmin)
admin.site.register(project_core.models.CallQuestion, CallQuestionAdmin)
admin.site.register(project_core.models.TemplateQuestion, TemplateQuestionAdmin)
admin.site.register(project_core.models.ProposalQAText, ProposalQATextAdmin)
admin.site.register(project_core.models.CareerStage, CareerStageAdmin)
admin.site.register(project_core.models.Role, RoleAdmin)
admin.site.register(project_core.models.ProposalPartner, ProposalPartnerAdmin)
admin.site.register(project_core.models.ProposalComment, ProposalCommentAdmin)
admin.site.register(project_core.models.CallComment, CallCommentAdmin)