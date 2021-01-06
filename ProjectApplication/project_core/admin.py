from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from simple_history.admin import SimpleHistoryAdmin

import project_core.models


# Not an admin but to add history fields on admin
# To use it just add:
# history_list_display = ('history_field_changes',)
# And inherit of SimpleHistoryAdminFieldChanges

class SimpleHistoryAdminFieldChanges:
    def history_field_changes(self, obj):
        description_changes = ''

        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)

            for field in delta.changed_fields:
                previous_value = escape(getattr(delta.old_record, field))
                new_value = escape(getattr(delta.new_record, field))
                description_changes += f'Field: {field} Prev: {previous_value} Current: {new_value}<br>'

        return mark_safe(description_changes)


class StepTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ('name', 'description',)


class StepAdmin(admin.ModelAdmin):
    list_display = ('call', 'step_type', 'date', 'created_on', 'modified_on',)
    ordering = ('call', 'step_type', 'date', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order',)
    ordering = ('name', 'order',)


class FundingInstrumentAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = ('long_name', 'short_name', 'description', 'created_on', 'modified_on',)
    ordering = ('long_name', 'short_name', 'description', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes',)


class CallAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'long_name', 'short_name', 'call_open_date', 'submission_deadline',
        # 'budget_categories_list',
        'budget_maximum', 'other_funding_question',
        'proposal_partner_question', 'overarching_project_question', 'scientific_clusters_question',
        'keywords_in_general_information_question', 'overall_budget_question',
        'created_on', 'modified_on',)
    ordering = ('long_name', 'short_name', 'call_open_date', 'submission_deadline', 'budget_maximum',
                'created_on', 'modified_on',)

    history_list_display = ('history_field_changes',)

    readonly_fields = ('created_on', 'modified_on',)

    # def budget_categories_list(self, obj):
    #     return 'TODO'
    #     budget_categories = obj.budget_categories.all()
    #
    #     return ", ".join([budget_category.name for budget_category in budget_categories])

    # def call_questions_list(self, obj):
    #     call_questions = obj.callquestion_set.all()
    #
    #     questions = ''
    #     for call_question in call_questions:
    #         questions += call_question.question_text
    #
    #     return questions


class BudgetCategoryCallAdmin(admin.ModelAdmin):
    list_display = ('call', 'budget_category', 'enabled', 'order',)
    ordering = ('call', 'budget_category', 'order',)


class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'uid', 'created_on', 'modified_on',)
    ordering = ('name', 'description', 'uid', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    search_fields = ('name', 'description',)
    raw_id_fields = ('uid',)


class KeywordUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_on', 'modified_on',)
    ordering = ('uid', 'source', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class ProposalStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ('description',)


class PersonTitleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)


class CountryUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_on', 'modified_on',)
    ordering = ('uid', 'source', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'created_on', 'modified_on',)
    ordering = ('name', 'uid', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class OrganisationUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_on', 'modified_on',)
    ordering = ('uid', 'source', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class OrganisationAdmin(admin.ModelAdmin):
    list_display = (
        'long_name', 'short_name', 'street', 'city', 'postal_code', 'country', 'uid', 'created_on',
        'modified_on',)
    ordering = ('long_name', 'short_name', 'city', 'country', 'uid', 'created_on',
                'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    search_fields = ('long_name', 'short_name', 'street', 'city', 'postal_code', 'country__name', 'uid',)


class OrganisationNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'organisation', 'created_on', 'modified_on',)
    ordering = ('name',)
    search_fields = ('name',)
    readonly_fields = ('created_on', 'modified_on',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('source', 'created_on', 'modified_on',)
    ordering = ('source', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class GenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on', 'modified_on',)
    ordering = ('name', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class PhysicalPersonAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'first_name', 'surname', 'orcid', 'gender', 'phd_date', 'created_on', 'modified_on',)
    ordering = ('first_name', 'surname', 'orcid', 'gender', 'phd_date', 'created_on',
                'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes',)
    search_fields = ('first_name', 'surname', 'orcid', 'phd_date',)


class PersonUidAdmin(admin.ModelAdmin):
    list_display = ('person', 'uid', 'source',)
    ordering = ('person', 'uid', 'source',)


class PersonPositionAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'person', 'academic_title', 'career_stage', 'organisations_list', 'group', 'privacy_policy',
        'contact_newsletter', 'created_on', 'modified_on',)
    ordering = ('person', 'academic_title', 'career_stage', 'group', 'privacy_policy', 'contact_newsletter',
                'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes',)

    def organisations_list(self, obj):
        organisation_names = obj.organisation_names.all()

        return ', '.join([str(organisation_name.name) for organisation_name in organisation_names])


class ContactAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = ('person_position', 'method', 'entry', 'created_on', 'modified_on',)
    ordering = ('person_position', 'method', 'entry', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes',)


class GeographicalAreaUidAdmin(admin.ModelAdmin):
    list_display = ('uid', 'source', 'created_on', 'modified_on',)
    ordering = ('uid', 'source', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class GeographicalAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'definition', 'uid', 'created_on', 'modified_on',)
    ordering = ('name', 'uid', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class ProposalAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = ('title', 'uuid', 'keywords_list', 'geographical_area_list', 'location', 'start_date',
                    'end_date', 'duration_months', 'applicant', 'proposal_status', 'eligibility', 'eligibility_comment',
                    'call', 'created_on', 'modified_on',
                    'draft_saved_mail_sent', 'submitted_mail_sent',)
    ordering = ('title', 'uuid', 'start_date', 'end_date', 'duration_months', 'applicant',
                'proposal_status', 'eligibility', 'eligibility_comment', 'call', 'created_on',
                'modified_on', 'draft_saved_mail_sent', 'submitted_mail_sent',)
    readonly_fields = ('created_on', 'modified_on',)

    history_list_display = ('history_field_changes',)

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
    ordering = ('details', 'amount', 'proposal',)
    search_fields = ('category__name', 'details', 'amount', 'proposal__title',)


class FundingStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'description',)
    ordering = ('status',)


class ProposalFundingItemAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'organisation_name', 'funding_status', 'amount',)
    ordering = ('proposal', 'organisation_name', 'funding_status', 'amount',)


class CallQuestionAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'call_part', 'question_text', 'question_description', 'answer_type', 'answer_max_length', 'order',
        'created_on', 'modified_on',)
    ordering = ('call_part', 'question_text', 'answer_type', 'answer_max_length', 'order', 'created_on',
                'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes',)


class TemplateQuestionAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'question_text', 'question_description', 'answer_type', 'answer_max_length', 'created_on',
        'modified_on',)
    ordering = ('question_text', 'answer_type', 'answer_max_length', 'created_on',
                'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes',)
    search_fields = ('question_text', 'question_description',)


class ProposalQATextAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'call_question', 'answer', 'created_on', 'modified_on',)
    ordering = ('proposal', 'call_question', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class CareerStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'list_order',)
    ordering = ('name', 'list_order',)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type',)
    ordering = ('name', 'type',)


class ProposalPartnerAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'person', 'role', 'role_description', 'competences',)
    ordering = ('proposal', 'person', 'role',)


class ProposalQAFileAdmin(admin.ModelAdmin):
    list_display = (
        'proposal', 'call_question', 'file', 'md5', 'created_on', 'modified_on',)
    ordering = ('proposal', 'call_question', 'file', 'md5', 'created_on', 'modified_on',)
    readonly_fields = ('created_on', 'modified_on',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'uuid', 'keywords_list', 'geographical_area_list', 'location', 'start_date',
                    'end_date', 'principal_investigator', 'call', 'proposal', 'overarching_project',
                    'allocated_budget', 'status', 'abortion_reason', 'created_on', 'modified_on',)
    ordering = ('title', 'uuid', 'location', 'start_date', 'end_date', 'principal_investigator',
                'call', 'proposal', 'allocated_budget', 'status', 'abortion_reason',)

    def keywords_list(self, obj):
        keywords = obj.keywords.all()

        return ", ".join([keyword.name for keyword in keywords])

    def geographical_area_list(self, obj):
        geographical_areas = obj.geographical_areas.all()

        return ", ".join([geographical_area.name for geographical_area in geographical_areas])


class ProjectPartnerAdmin(admin.ModelAdmin):
    list_display = ('project', 'person', 'role', 'role_description', 'competences',)
    ordering = ('project', 'person', 'role',)


class FinancialKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'funding_instrument', 'created_on', 'created_by',)
    ordering = ('name', 'description', 'created_on',)


class PostalAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'city', 'postcode', 'country',)
    ordering = ('address', 'city', 'postcode', 'country__name',)
    search_fields = ('address', 'city', 'postcode', 'country__name',)


class RoleDescriptionAdmin(admin.ModelAdmin):
    list_display = ('role', 'description', 'competences',)
    ordering = ('role', 'description', 'competences',)


class CallPartAdmin(admin.ModelAdmin):
    list_display = ('call', 'title', 'introductory_text')


class CallPartFileAdmin(admin.ModelAdmin):
    list_display = ('call_part', 'name', 'description', 'file',)


admin.site.register(project_core.models.StepType, StepTypeAdmin)
admin.site.register(project_core.models.Step, StepAdmin)
admin.site.register(project_core.models.BudgetCategory, BudgetCategoryAdmin)
admin.site.register(project_core.models.FundingInstrument, FundingInstrumentAdmin)
admin.site.register(project_core.models.Call, CallAdmin)
admin.site.register(project_core.models.BudgetCategoryCall, BudgetCategoryCallAdmin)
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
admin.site.register(project_core.models.Project, ProjectAdmin)
admin.site.register(project_core.models.ProjectPartner, ProjectPartnerAdmin)
admin.site.register(project_core.models.FinancialKey, FinancialKeyAdmin)
admin.site.register(project_core.models.PostalAddress, PostalAddressAdmin)
admin.site.register(project_core.models.RoleDescription, RoleDescriptionAdmin)
admin.site.register(project_core.models.CallPart, CallPartAdmin)
admin.site.register(project_core.models.CallPartFile, CallPartFileAdmin)
