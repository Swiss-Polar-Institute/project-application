from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from project_core.admin import SimpleHistoryAdminFieldChanges
from .models import Reviewer, ProposalEvaluation, CallEvaluation


class ProposalEvaluationAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'proposal', 'allocated_budget', 'panel_remarks', 'feedback_to_applicant', 'panel_recommendation',
        'board_decision', 'decision_date', 'created_on', 'modified_on')
    readonly_fields = ('created_on', 'modified_on',)
    history_list_display = ['history_field_changes']


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'calls_list')
    filter_horizontal = ('calls',)

    def calls_list(self, obj):
        return ', '.join([str(call) for call in obj.calls.all()])


class CallEvaluationAdmin(admin.ModelAdmin):
    list_display = ('call', 'panel_date', 'evaluation_sheet')


admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(ProposalEvaluation, ProposalEvaluationAdmin)
admin.site.register(CallEvaluation, CallEvaluationAdmin)
