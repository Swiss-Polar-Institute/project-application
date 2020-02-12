from django.urls import reverse

from comments.forms.attachment import AttachmentForm
from comments.forms.comment import CommentForm


def adds_comment_attachment_forms(context, submit_viewname, parent_id, comment_category_queryset, attachment_category_queryset):
    context[CommentForm.FORM_NAME] = CommentForm(form_action=reverse(submit_viewname,
                                                                     kwargs={'id': parent_id}),
                                                 category_queryset=comment_category_queryset,
                                                 prefix=CommentForm.FORM_NAME)

    context[AttachmentForm.FORM_NAME] = AttachmentForm(form_action=reverse(submit_viewname,
                                                                           kwargs={'id': parent_id}),
                                                       category_queryset=attachment_category_queryset,
                                                       prefix=AttachmentForm.FORM_NAME)
