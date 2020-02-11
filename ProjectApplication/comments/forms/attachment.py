from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms

from ..models import ProposalAttachment, ProposalAttachmentCategory


class AttachmentForm(forms.Form):
    # Note that Comments are not editable, so initial is always empty, always a new comment
    def __init__(self, *args, **kwargs):
        form_action = kwargs.pop('form_action')

        super().__init__(*args, **kwargs)

        self.fields['category'] = forms.ModelChoiceField(label='Category',
                                                         queryset=ProposalAttachmentCategory.objects.all(),
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
        proposal_attachment.comment_text = self.cleaned_data['text']
        proposal_attachment.created_by = user
        proposal_attachment.category = self.cleaned_data['category']
        proposal_attachment.file = self.cleaned_data['file']

        proposal_attachment.save()
