from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from project_core.admin import SimpleHistoryAdminFieldChanges
from .models import Reviewer, ProposalEvaluation


class ProposalEvaluationAdmin(SimpleHistoryAdmin, SimpleHistoryAdminFieldChanges):
    list_display = (
        'proposal', 'final_mark', 'allocated_budget', 'panel_remarks', 'feedback_to_applicant', 'panel_recommendation',
        'board_decision', 'decision_date', 'created_on', 'modified_on')
    history_list_display = ['allocated_budget', 'panel_remarks', ]
    readonly_fields = ('created_on', 'modified_on',)


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'calls_list')
    filter_horizontal = ('calls',)

    def calls_list(self, obj):
        return ', '.join([str(call) for call in obj.calls.all()])


admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(ProposalEvaluation, ProposalEvaluationAdmin)
