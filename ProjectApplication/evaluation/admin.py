from django.contrib import admin

from .models import Reviewer, ProposalEvaluation
from simple_history.admin import SimpleHistoryAdmin


class ProposalEvaluationAdmin(SimpleHistoryAdmin):
    list_display = (
        'proposal', 'final_mark', 'allocated_budget', 'panel_remarks', 'feedback_to_applicant', 'panel_recommendation',
        'board_decision', 'decision_date')
    history_list_display = ['allocated_budget', 'panel_remarks', ]


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'calls_list')
    filter_horizontal = ('calls',)

    def calls_list(self, obj):
        return ', '.join([str(call) for call in obj.calls.all()])


admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(ProposalEvaluation, ProposalEvaluationAdmin)
