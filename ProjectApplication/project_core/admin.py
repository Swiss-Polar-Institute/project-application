from django.contrib import admin
from django.forms import ModelForm, TextInput

import project_core.models


class StepTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['name', 'description', ]


class StepAdmin(admin.ModelAdmin):
    list_display = ('call', 'step_type', 'date', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['call', 'step_type', 'date', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order',)
    ordering = ['name', 'order', ]


class FundingInstrumentAdmin(admin.ModelAdmin):
    list_display = ('long_name', 'short_name', 'description', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['long_name', 'short_name', 'description', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class CallAdmin(admin.ModelAdmin):
    list_display = (
        'long_name', 'short_name', 'description', 'introductory_message', 'call_open_date', 'submission_deadline',
        'budget_categories_list', 'budget_maximum', 'call_questions_list', 'other_funding_question',
        'proposal_partner_question', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['long_name', 'short_name', 'call_open_date', 'submission_deadline', 'budget_maximum', 'created_by',
                'created_on', 'modified_by', 'modified_on', ]

    def budget_categories_list(self, obj):
        budget_categories = obj.budget_categories.all()

        return ", ".join([budget_category.name for budget_category in budget_categories])

    filter_vertical = ('budget_categories',)

    def call_questions_list(self, obj):
        call_questions = obj.callquestion_set.all()

        questions = ''
        for call_question in call_questions:
            questions += call_question.question_text

        return questions


class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'uid', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['name', 'description', 'uid', 'created_by', 'created_on', 'modified_by', 'modified_on', ]
    readonly_fields = ('created_on', 'modified_on',)
    search_fields = ('name', 'description',)
    raw_id_fields = ('uid',)


class KeywordUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on', ]
    readonly_fields = ('created_on', 'modified_on',)


class ProposalStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['description', ]


class PersonTitleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ['title', ]


class CountryUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['name', 'uid', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class OrganisationUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class OrganisationAdmin(admin.ModelAdmin):
    list_display = (
        'long_name', 'short_name', 'street', 'city', 'postal_code', 'country', 'uid', 'created_by', 'created_on',
        'modified_by', 'modified_on',)
    ordering = ['long_name', 'short_name', 'city', 'country', 'uid', 'created_by', 'created_on', 'modified_by',
                'modified_on', ]


class OrganisationNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'organisation', 'created_by', 'created_on', 'modified_by', 'modified_on')
    ordering = ['name']
    search_fields = ('name',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('source', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['source', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class GenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['name', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class PhysicalPersonAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'surname', 'gender', 'phd_date', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['first_name', 'surname', 'gender', 'phd_date', 'created_by', 'created_on', 'modified_by',
                'modified_on', ]


class PersonUidAdmin(admin.ModelAdmin):
    list_display = ('person', 'uid', 'source',)
    ordering = ['person', 'uid', 'source', ]


class PersonPositionAdmin(admin.ModelAdmin):
    list_display = (
        'person', 'academic_title', 'career_stage', 'organisations_list', 'group', 'privacy_policy',
        'contact_newsletter',
        'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['person', 'academic_title', 'career_stage', 'group', 'privacy_policy', 'contact_newsletter',
                'created_by', 'created_on', 'modified_by', 'modified_on', ]

    def organisations_list(self, obj):
        organisation_names = obj.organisation_names.all()

        return ', '.join([str(organisation_name.name) for organisation_name in organisation_names])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('person_position', 'method', 'entry', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['person_position', 'method', 'entry', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class GeographicalAreaUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['uid', 'source', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class GeographicalAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'definition', 'uid', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['name', 'uid', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'uuid', 'keywords_list', 'geographical_area_list', 'location', 'start_date',
                    'end_date', 'duration_months', 'applicant', 'proposal_status', 'eligibility', 'eligibility_comment',
                    'qas_list', 'call', 'created_by', 'created_on', 'modified_by', 'modified_on',
                    'draft_saved_mail_sent', 'submitted_mail_sent',)
    ordering = ['title', 'uuid', 'start_date', 'end_date', 'duration_months', 'applicant',
                'proposal_status', 'eligibility', 'eligibility_comment', 'call', 'created_by', 'created_on',
                'modified_by', 'modified_on',
                'draft_saved_mail_sent', 'submitted_mail_sent', ]

    # Search at the moment only works without '-'
    search_fields = ('title', 'uuid',)

    def keywords_list(self, obj):
        keywords = obj.keywords.all()

        return ", ".join([keyword.name for keyword in keywords])

    def geographical_area_list(self, obj):
        geographical_areas = obj.geographical_areas.all()

        return ", ".join([geographical_area.name for geographical_area in geographical_areas])

    def qas_list(self, obj):
        qas = obj.proposalqatext_set.all()

        result = ''
        for qa in qas:
            qa: project_core.models.ProposalQAText

            result += 'Q: {}, A: {}'.format(qa.call_question.question_text, qa.answer)

        return result


class ProposedBudgetItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'details', 'amount', 'proposal',)
    ordering = ['details', 'amount', 'proposal', ]
    search_fields = ('category__name', 'details', 'amount', 'proposal__title',)


class FundingStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'description',)
    ordering = ['status', ]


class ProposalFundingItemAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'organisation_name', 'funding_status', 'amount')
    ordering = ['proposal', 'organisation_name', 'funding_status', 'amount', ]


class CallQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'call', 'question_text', 'question_description', 'answer_type', 'answer_max_length', 'order', 'created_by',
        'created_on', 'modified_by', 'modified_on',)
    ordering = ['call', 'question_text', 'answer_type', 'answer_max_length', 'order', 'created_by', 'created_on',
                'modified_by', 'modified_on', ]


class TemplateQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'question_text', 'question_description', 'answer_type', 'answer_max_length', 'created_by', 'created_on',
        'modified_by', 'modified_on',)
    ordering = ['question_text', 'answer_type', 'answer_max_length', 'created_by', 'created_on', 'modified_by',
                'modified_on', ]


class ProposalQATextAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'call_question', 'answer', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['proposal', 'call_question', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class CareerStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ['name', ]


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type')
    ordering = ['name', 'type', ]


class ProposalPartnerAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'person', 'role', 'role_description', 'competences')
    ordering = ['proposal', 'person', 'role', ]


class ProposalQAFileAdmin(admin.ModelAdmin):
    list_display = (
        'proposal', 'call_question', 'file', 'md5', 'created_by', 'created_on', 'modified_by', 'modified_on',)
    ordering = ['proposal', 'call_question', 'file', 'md5', 'created_by', 'created_on', 'modified_by', 'modified_on']


class ColourForm(ModelForm):
    class Meta:
        model = project_core.models.Colour
        fields = '__all__'
        widgets = {
            'hex_code': TextInput(attrs={'type': 'color'}),
        }


class ColourAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    ordering = ['name', 'hex_code']
    form = ColourForm


admin.site.register(project_core.models.StepType, StepTypeAdmin)
admin.site.register(project_core.models.Step, StepAdmin)
admin.site.register(project_core.models.BudgetCategory, BudgetCategoryAdmin)
admin.site.register(project_core.models.FundingInstrument, FundingInstrumentAdmin)
admin.site.register(project_core.models.Call, CallAdmin)
admin.site.register(project_core.models.Keyword, KeywordAdmin)
admin.site.register(project_core.models.KeywordUid, KeywordUidAdmin)
admin.site.register(project_core.models.ProposalStatus, ProposalStatusAdmin)
admin.site.register(project_core.models.PersonTitle, PersonTitleAdmin)
admin.site.register(project_core.models.CountryUid, CountryUidAdmin)
admin.site.register(project_core.models.Country, CountryAdmin)
admin.site.register(project_core.models.OrganisationUid, OrganisationUidAdmin)
admin.site.register(project_core.models.Organisation, OrganisationAdmin)
admin.site.register(project_core.models.OrganisationName, OrganisationNameAdmin)
admin.site.register(project_core.models.Source, SourceAdmin)
admin.site.register(project_core.models.PersonUid, PersonUidAdmin)
admin.site.register(project_core.models.Gender, GenderAdmin)
admin.site.register(project_core.models.PhysicalPerson, PhysicalPersonAdmin)
admin.site.register(project_core.models.PersonPosition, PersonPositionAdmin)
admin.site.register(project_core.models.Contact, ContactAdmin)
admin.site.register(project_core.models.GeographicalAreaUid, GeographicalAreaUidAdmin)
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
admin.site.register(project_core.models.ProposalQAFile, ProposalQAFileAdmin)
admin.site.register(project_core.models.Colour, ColourAdmin)
