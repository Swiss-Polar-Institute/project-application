from django.contrib import admin

import comments.models


class ProposalCommentAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'text', 'created_by', 'created_on',)
    ordering = ['proposal', 'text', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class CallCommentAdmin(admin.ModelAdmin):
    list_display = ('call', 'text', 'created_by', 'created_on',)
    ordering = ['call', 'text', 'created_by', 'created_on', 'modified_by', 'modified_on', ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'colour', 'created_by', 'created_on',)
    ordering = ['category']


class ProposalCommentCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'created_by', 'created_on',)
    ordering = ['category', ]


class ProposalAttachmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'created_by', 'created_on',)
    ordering = ['category', ]


class ProposalAttachmentAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'file', 'created_by', 'created_on',)


class CallAttachmentAdmin(admin.ModelAdmin):
    list_display = ('call', 'file', 'created_by', 'created_on',)


class CallAttachmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'created_by', 'created_on',)


class CallCommentCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'created_by', 'created_on',)
    ordering = ['category', ]


admin.site.register(comments.models.ProposalComment, ProposalCommentAdmin)
admin.site.register(comments.models.CallComment, CallCommentAdmin)
admin.site.register(comments.models.Category, CategoryAdmin)
admin.site.register(comments.models.ProposalCommentCategory, ProposalCommentCategoryAdmin)
admin.site.register(comments.models.ProposalAttachmentCategory, ProposalAttachmentCategoryAdmin)
admin.site.register(comments.models.ProposalAttachment, ProposalAttachmentAdmin)
admin.site.register(comments.models.CallAttachment, CallAttachmentAdmin)
admin.site.register(comments.models.CallAttachmentCategory, CallAttachmentCategoryAdmin)
admin.site.register(comments.models.CallCommentCategory, CallCommentCategoryAdmin)
