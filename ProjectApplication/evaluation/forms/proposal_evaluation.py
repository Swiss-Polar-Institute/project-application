from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse
from django.utils.formats import number_format

from ProjectApplication import settings
from project_core.forms.utils import cancel_edit_button
from project_core.utils import user_is_in_group_name
from project_core.widgets import XDSoftYearMonthDayPickerInput
from ..models import ProposalEvaluation, Reviewer


class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.person


class ProposalEvaluationForm(forms.ModelForm):
    FORM_NAME = 'proposal_evaluation_form'

    def __init__(self, *args, **kwargs):
        assert 'instance' not in kwargs

        self._proposal = kwargs.pop('proposal')

        try:
            proposal_evaluation = ProposalEvaluation.objects.get(proposal=self._proposal)
            kwargs['instance'] = proposal_evaluation
        except ObjectDoesNotExist:
            pass

        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_action = reverse('logged-proposal-evaluation-update', kwargs={'pk': self._proposal.id})

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['decision_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['decision_letter_date'])
        self.fields['proposal'].initial = self._proposal
        requested_budget = number_format(self._proposal.total_budget())

        self.fields['allocated_budget'] = forms.DecimalField(localize=True, required=False)
        self.fields['allocated_budget'].help_text = f'Requested: {requested_budget} CHF'
        self.fields['allocated_budget'].label = 'Allocated budget (CHF)'

        if self._proposal.proposalevaluation:
            initial_reviewers = self._proposal.reviewer_set.all()
        else:
            initial_reviewers = []

        self.fields['reviewers'] = ModelMultipleChoiceField(initial=initial_reviewers,
                                                            queryset=Reviewer.objects.all(),
                                                            required=True,
                                                            widget=FilteredSelectMultiple(
                                                                is_stacked=True,
                                                                verbose_name='reviewers'))

        if hasattr(self._proposal, 'proposalevaluation'):
            cancel_button_url = reverse('logged-proposal-evaluation-detail',
                                        kwargs={'pk': self._proposal.proposalevaluation.id})
        else:
            cancel_button_url = reverse('logged-proposal-evaluation-add') + f'?proposal={self._proposal.id}'

        self.helper.layout = Layout(
            Div(
                Div('proposal', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('reviewers', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('panel_remarks', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('feedback_to_applicant', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('panel_recommendation', css_class='col-6'),
                Div('allocated_budget', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('board_decision', css_class='col-6'),
                Div('decision_date', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('decision_letter', css_class='col-6'),
                Div('decision_letter_date', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Evaluation'),
                cancel_edit_button(cancel_button_url)
            )
        )

    def clean(self):
        super().clean()

        decision_letter_date = self.cleaned_data.get('decision_letter_date', None)
        decision_letter = self.cleaned_data.get('decision_letter', None)
        panel_recommendation = self.cleaned_data.get('panel_recommendation', None)
        board_decision = self.cleaned_data.get('board_decision', None)
        allocated_budget = self.cleaned_data.get('allocated_budget', None)
        decision_date = self.cleaned_data.get('decision_date', None)

        errors = {}
        if decision_letter and decision_letter_date is None:
            errors['decision_letter_date'] = forms.ValidationError(
                'A decision letter date is required if there is a decision letter attached')

        if decision_letter_date and decision_letter is None:
            errors['decision_letter'] = forms.ValidationError(
                'A decision letter is required if there is a decision letter date')

        if panel_recommendation in (ProposalEvaluation.PANEL_RECOMMENDATION_FUND,
                                    ProposalEvaluation.PANEL_RECOMMENDATION_RESERVE) and allocated_budget is None:
            errors['allocated_budget'] = forms.ValidationError(
                'An allocated budget is required if the panel decision is to fund or keep the proposal as a reserve')

        if board_decision and decision_date is None:
            errors['decision_date'] = forms.ValidationError(
                'A decision date is required if the board has made a decision')

        if errors:
            raise forms.ValidationError(errors)

    def save(self, *args, **kwargs):
        user = kwargs.pop('user')

        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        reviewers = self.cleaned_data['reviewers']

        proposal_evaluation = super().save(*args, **kwargs)

        proposal_evaluation.proposal.reviewer_set.set(reviewers)

        return proposal_evaluation

    class Meta:
        model = ProposalEvaluation

        fields = ['proposal', 'allocated_budget', 'panel_remarks', 'feedback_to_applicant',
                  'panel_recommendation', 'board_decision', 'decision_date', 'decision_letter',
                  'decision_letter_date']
        widgets = {
            'proposal': forms.HiddenInput,
            'decision_date': XDSoftYearMonthDayPickerInput,
            'decision_letter_date': XDSoftYearMonthDayPickerInput,
        }
