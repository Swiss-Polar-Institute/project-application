from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse

from ..models import ProposalComment
from project_core.models import Proposal


class CommentForm(forms.Form):
    # Note that Comments are not editable, so initial is always empty, always a new comment
    def __init__(self, *args, **kwargs):
        form_action = kwargs.pop('form_action')

        super().__init__(*args, **kwargs)

        self.fields['text'] = forms.CharField(label='Add comment', max_length=1000, help_text='Write the comment',
                                                 widget=forms.Textarea(attrs={'rows': 4}))

        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.add_input(Submit('submit', 'Save comment', css_class='btn-primary'))

        self.helper.layout = Layout(
            Div(
                Div('text', css_class='col-12'),
                css_class='row'
            )
        )

    def save_into_proposal(self, proposal, user):
        proposal_comment = ProposalComment()
        proposal_comment.proposal = proposal
        proposal_comment.text = self.cleaned_data['text']
        proposal_comment.created_by = user

        proposal_comment.save()
