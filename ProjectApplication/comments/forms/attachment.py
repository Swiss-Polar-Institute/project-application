import logging

import botocore
from botocore.exceptions import EndpointConnectionError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms

from ..models import ProposalAttachment, ProposalAttachmentCategory, CallAttachment

logger = logging.getLogger('comments')


class AttachmentForm(forms.Form):
    ATTACHMENT_FORM_NAME = 'attachment_form'

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

    def save_into_proposal(self, proposal, user):
        proposal_attachment = ProposalAttachment()

        proposal_attachment.proposal = proposal
        proposal_attachment.text = self.cleaned_data['text']
        proposal_attachment.created_by = user
        proposal_attachment.category = self.cleaned_data['category']

        file = self.cleaned_data['file']

        if not file.name.startswith('/'):
            file.name = f'{proposal.id}-{file.name}'

        proposal_attachment.file = self.cleaned_data['file']

        all_good = True
        try:
            proposal_attachment.save()
        except EndpointConnectionError:
            all_good = False
            logger.warning(
                f'NOTIFY: Saving attachment to proposal failed (proposal: {proposal.id} User: {user}) -EndpointConnectionError')
        except botocore.exceptions.ClientError:
            all_good = False
            logger.warning(
                f'NOTIFY: Saving file for question failed (proposal: {proposal.id}  User: {user} -ClientError')

        return all_good

    def save_into_call(self, call, user):
        call_attachment = CallAttachment()

        call_attachment.call = call
        call_attachment.text = self.cleaned_data['text']
        call_attachment.created_by = user
        call_attachment.category = self.cleaned_data['category']

        file = self.cleaned_data['file']

        if not file.name.startswith('/'):
            file.name = f'{call.id}-{file.name}'

        call_attachment.file = self.cleaned_data['file']

        all_good = True
        try:
            call_attachment.save()
        except EndpointConnectionError:
            all_good = False
            logger.warning(
                f'NOTIFY: Saving attachment to call failed (proposal: {call.id} User: {user}) -EndpointConnectionError')
        except botocore.exceptions.ClientError:
            all_good = False
            logger.warning(
                f'NOTIFY: Saving file for question failed (proposal: {call.id}  User: {user} -ClientError')

        return all_good
