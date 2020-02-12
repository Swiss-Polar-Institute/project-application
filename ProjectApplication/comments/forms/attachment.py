import logging

import botocore
from botocore.exceptions import EndpointConnectionError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms

from ..models import ProposalAttachment, ProposalAttachmentCategory, CallAttachment

logger = logging.getLogger('comments')


class AttachmentForm(forms.Form):
    FORM_NAME = 'attachment_form'

    # Note that Comments are not editable, so initial is always empty, always a new comment
    def __init__(self, *args, **kwargs):
        form_action = kwargs.pop('form_action')
        category_queryset =  kwargs.pop('category_queryset')

        super().__init__(*args, **kwargs)

        self.fields['category'] = forms.ModelChoiceField(label='Category',
                                                         queryset=category_queryset,
                                                         help_text='Select category of comment')

        self.fields['file'] = forms.FileField(label='Attachment', help_text='File to attach')

        self.fields['text'] = forms.CharField(label='Text', max_length=10000,
                                              help_text='Write a comment of the file (max length: 10000 characters)',
                                              required=False,
                                              widget=forms.Textarea(attrs={'rows': 4}))

        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.add_input(Submit('attachment_form_submit', 'Save file', css_class='btn-primary'))

        self.helper.layout = Layout(
            Div(
                Div('category', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('file', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('text', css_class='col-12'),
                css_class='row'
            )
        )

    def save(self, parent, user):
        attachment = parent.attachment_object()()

        attachment.set_parent(parent)

        attachment.text = self.cleaned_data['text']
        attachment.created_by = user
        attachment.category = self.cleaned_data['category']

        file = self.cleaned_data['file']

        if not file.name.startswith('/'):
            file.name = f'{parent.id}-{file.name}'

        attachment.file = self.cleaned_data['file']

        all_good = True
        try:
            attachment.save()
        except EndpointConnectionError:
            all_good = False
            logger.warning(
                f'NOTIFY: Saving attachment failed (parent {type(parent)}: {parent.id} User: {user}) -EndpointConnectionError')
        except botocore.exceptions.ClientError:
            all_good = False
            logger.warning(
                f'NOTIFY: Saving attachment failed (parent: {type(parent)} {parent.id}  User: {user} -ClientError')

        return all_good
