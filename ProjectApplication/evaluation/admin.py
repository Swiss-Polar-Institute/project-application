from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from project_core.admin import SimpleHistoryAdminFieldChanges
from .models import Reviewer, ProposalEvaluation, CallEvaluation, Criterion, CriterionCallEvaluation


class ProposalEvaluationAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'proposal', 'allocated_budget', 'panel_remarks', 'feedback_to_applicant', 'panel_recommendation',
        'board_decision', 'decision_date', 'created_on', 'modified_on')
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ('history_field_changes', )


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'person', 'call_list', 'proposal_list',)
    filter_vertical = ('calls', 'proposals',)

    def call_list(self, obj):
        return ', '.join([str(call) for call in obj.calls.all()])

    def proposal_list(self, obj):
        return ', '.join([str(proposal) for proposal in obj.proposals.all()])


class CallEvaluationAdmin(admin.ModelAdmin):
    list_display = ('call', 'panel_date', 'post_panel_management_table', 'closed_date', 'closed_user')


class CriterionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class CriterionCallEvaluationAdmin(admin.ModelAdmin):
    list_display = ('call_evaluation', 'criterion', 'enabled', 'order')


admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(ProposalEvaluation, ProposalEvaluationAdmin)
admin.site.register(CallEvaluation, CallEvaluationAdmin)
admin.site.register(Criterion, CriterionAdmin)
admin.site.register(CriterionCallEvaluation, CriterionCallEvaluationAdmin)
