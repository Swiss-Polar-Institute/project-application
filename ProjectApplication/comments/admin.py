from django.contrib import admin

import comments.models


class ProposalCommentAdmin(admin.ModelAdmin):
    search_fields = ('proposal__title', 'text', )
    list_display = ('proposal', 'text', 'created_by', 'created_on',)
    ordering = ('proposal', 'text', 'created_on', 'modified_on',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'colour__description',)
    list_display = ('name', 'colour', 'created_on',)
    ordering = ('name', 'colour', 'created_on',)


class ProposalCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class ProposalAttachmentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class ProposalAttachmentAdmin(admin.ModelAdmin):
    search_fields = ('proposal__title', 'file', )
    list_display = ('proposal', 'file', 'created_by', 'created_on',)
    ordering = ('proposal', 'file', 'created_by', 'created_on',)


class CallAttachmentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name',)
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class CallAttachmentAdmin(admin.ModelAdmin):
    search_fields = ('call__long_name', 'file',)
    list_display = ('call', 'file', 'created_by', 'created_on',)
    ordering = ('call', 'file', 'created_by', 'created_on',)


class CallCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name',)
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class CallCommentAdmin(admin.ModelAdmin):
    search_fields = ('call__long_name', 'text',)
    list_display = ('call', 'text', 'created_by', 'created_on',)
    ordering = ('call', 'text', 'created_on', 'modified_on',)


class ProposalEvaluationAttachmentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class ProposalEvaluationAttachmentAdmin(admin.ModelAdmin):
    search_fields = ('proposal_evaluation__proposal__title', 'file', )
    list_display = ('proposal_evaluation', 'file', 'created_by', 'created_on',)
    ordering = ('proposal_evaluation', 'file', 'created_by', 'created_on',)


class ProposalEvaluationCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class ProposalEvaluationCommentAdmin(admin.ModelAdmin):
    search_fields = ('proposal_evaluation__proposal__title', 'text', )
    list_display = ('proposal_evaluation', 'text', 'created_by', 'created_on')
    ordering = ('proposal_evaluation', 'text', 'created_by', 'created_on')


class CallEvaluationCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name',)
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class CallEvaluationCommentAdmin(admin.ModelAdmin):
    search_fields = ('call_evaluation__call__long_name', 'text',)
    list_display = ('call_evaluation', 'text', 'created_by', 'created_on')
    ordering = ('call_evaluation', 'text', 'created_by', 'created_on')


class ProjectAttachmentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class ProjectAttachmentAdmin(admin.ModelAdmin):
    search_fields = ('project__title', 'file', )
    list_display = ('project', 'file', 'created_by', 'created_on',)
    ordering = ('project', 'file', 'created_by', 'created_on',)


class ProjectCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class ProjectCommentAdmin(admin.ModelAdmin):
    search_fields = ('project__title', 'text', )
    list_display = ('project', 'text', 'created_by', 'created_on')
    ordering = ('project', 'text', 'created_by', 'created_on')


class InvoiceCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name', )
    list_display = ('category', 'created_on')
    ordering = ('category', 'created_on')


class InvoiceCommentAdmin(admin.ModelAdmin):
    search_fields = ('invoice__id', 'invoice__amount', 'text', )
    list_display = ('invoice', 'text', 'created_by', 'created_on')
    ordering = ('invoice', 'text', 'created_by', 'created_on')


class GrantAgreementAttachmentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name',)
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class GrantAgreementAttachmentAdmin(admin.ModelAdmin):
    search_fields = ('grant_agreement__project__title', 'file',)
    list_display = ('grant_agreement', 'file', 'created_by', 'created_on',)
    ordering = ('grant_agreement', 'file', 'created_by', 'created_on',)


class GrantAgreementCommentCategoryAdmin(admin.ModelAdmin):
    search_fields = ('category__name',)
    list_display = ('category', 'created_on',)
    ordering = ('category', 'created_on',)


class GrantAgreementCommentAdmin(admin.ModelAdmin):
    search_fields = ('grant_agreement__project__title', 'text',)
    list_display = ('grant_agreement', 'text', 'created_by', 'created_on')
    ordering = ('grant_agreement', 'text', 'created_by', 'created_on')


admin.site.register(comments.models.Category, CategoryAdmin)

admin.site.register(comments.models.ProposalCommentCategory, ProposalCommentCategoryAdmin)
admin.site.register(comments.models.ProposalComment, ProposalCommentAdmin)
admin.site.register(comments.models.ProposalAttachmentCategory, ProposalAttachmentCategoryAdmin)
admin.site.register(comments.models.ProposalAttachment, ProposalAttachmentAdmin)

admin.site.register(comments.models.CallCommentCategory, CallCommentCategoryAdmin)
admin.site.register(comments.models.CallComment, CallCommentAdmin)
admin.site.register(comments.models.CallAttachmentCategory, CallAttachmentCategoryAdmin)
admin.site.register(comments.models.CallAttachment, CallAttachmentAdmin)

admin.site.register(comments.models.ProposalEvaluationCommentCategory, ProposalEvaluationCommentCategoryAdmin)
admin.site.register(comments.models.ProposalEvaluationComment, ProposalEvaluationCommentAdmin)
admin.site.register(comments.models.ProposalEvaluationAttachmentCategory, ProposalEvaluationAttachmentCategoryAdmin)
admin.site.register(comments.models.ProposalEvaluationAttachment, ProposalEvaluationAttachmentAdmin)

admin.site.register(comments.models.ProjectCommentCategory, ProjectCommentCategoryAdmin)
admin.site.register(comments.models.ProjectComment, ProjectCommentAdmin)
admin.site.register(comments.models.ProjectAttachmentCategory, ProjectAttachmentCategoryAdmin)
admin.site.register(comments.models.ProjectAttachment, ProjectAttachmentAdmin)

admin.site.register(comments.models.CallEvaluationCommentCategory, CallEvaluationCommentCategoryAdmin)
admin.site.register(comments.models.CallEvaluationComment, CallEvaluationCommentAdmin)

admin.site.register(comments.models.InvoiceCommentCategory, InvoiceCommentCategoryAdmin)
admin.site.register(comments.models.InvoiceComment, InvoiceCommentAdmin)

admin.site.register(comments.models.GrantAgreementCommentCategory, GrantAgreementCommentCategoryAdmin)
admin.site.register(comments.models.GrantAgreementComment, GrantAgreementCommentAdmin)
admin.site.register(comments.models.GrantAgreementAttachmentCategory, GrantAgreementAttachmentCategoryAdmin)
admin.site.register(comments.models.GrantAgreementAttachment, GrantAgreementAttachmentAdmin)
