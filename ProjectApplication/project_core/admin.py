from django.contrib import admin
import project_core.models


# Register your models here.


class StepAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['name', 'description',]


class StepDateAdmin(admin.ModelAdmin):
    list_display = ('step', 'date',)
    ordering = ['step', 'date',]


class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'message',)
    ordering = ['message_type',]


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
    list_display = ('long_name', 'short_name', 'address', 'country',)
    ordering = ['long_name', 'short_name', 'country',]


class PersonAdmin(admin.ModelAdmin):
    list_display = ('academic_title', 'first_name', 'surname', 'organisations_list', 'group',)
    ordering = ['academic_title', 'first_name', 'surname',]

    def organisations_list(self, obj):
        organisations = obj.organisations.all()

        return ", ".join([organisation.name for organisation in organisations])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'work_telephone', 'mobile', 'person',)
    ordering = ['email_address', 'work_telephone', 'mobile', 'person',]


class GeographicalAreaAdmin(admin.ModelAdmin):
    list_display = ('area', 'definition',)
    ordering = ['area',]


class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'keywords_list', 'geographical_area_list', 'location', 'start_timeframe', 'duration', 'applicant', 'proposal_status', 'qas_list', 'call')
    ordering = ['title', 'start_timeframe', 'duration', 'applicant', 'proposal_status', 'call',]

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
            result += 'Q: {}, A: {}'.format(qa.question.question_text, qa.answer)

        return result


class ProposedBudgetItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'details', 'amount', 'proposal', )
    ordering = ['details', 'amount', 'proposal', ]
    search_fields = ('category__name', 'details', 'amount', 'proposal__title', )


class FundingStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'description', )
    ordering = ['status', ]


class ProposalFundingItemAdmin(admin.ModelAdmin):
    list_display = ('proposal', )
    ordering = ['proposal', ]


class CallQuestionAdmin(admin.ModelAdmin):
    list_display = ('call', 'question_text', 'answer_type', 'answer_max_length')
    ordering = ['call', 'question_text', 'answer_type', 'answer_max_length']


class ProposalQATextAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'call_question', 'answer',)
    ordering = ['proposal', 'call_question',]


admin.site.register(project_core.models.Step, StepAdmin)
admin.site.register(project_core.models.StepDate, StepDateAdmin)
admin.site.register(project_core.models.Message, MessageAdmin)
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
admin.site.register(project_core.models.ProposalQAText, ProposalQATextAdmin)