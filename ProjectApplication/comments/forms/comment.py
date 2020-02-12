from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms

from ..models import ProposalComment, ProposalCommentCategory


class CommentForm(forms.Form):
    FORM_NAME = 'comment_form'
    # Note that Comments are not editable, so initial is always empty, always a new comment
    def __init__(self, *args, **kwargs):
        comment_category = kwargs.pop('category_queryset')
        form_action = kwargs.pop('form_action')

        super().__init__(*args, **kwargs)

        self.fields['category'] = forms.ModelChoiceField(label='Category', queryset=comment_category,
                                                     help_text='Select category of comment',)
        self.fields['text'] = forms.CharField(label='Text', max_length=10000,
                                              help_text='Write the comment (max length: 10000 characters)',
                                              widget=forms.Textarea(attrs={'rows': 4}))

        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.add_input(Submit('comment_form_submit', 'Save comment', css_class='btn-primary'))

        self.helper.layout = Layout(
            Div(
                Div('category', css_class='col-12'),
                css_class='row'
            ),
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
        proposal_comment.category = self.cleaned_data['category']

        proposal_comment.save()
