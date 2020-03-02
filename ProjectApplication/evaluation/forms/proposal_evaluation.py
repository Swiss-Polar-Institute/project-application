from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse
from django.utils.formats import number_format

from ProjectApplication import settings
from project_core.utils import user_is_in_group_name
from project_core.widgets import XDSoftYearMonthDayPickerInput
from ..models import ProposalEvaluation


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
        self.helper.form_action = reverse('logged-proposal-evaluation-update', kwargs={'uuid': self._proposal.uuid})
        self.helper.form_tag = False

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['decision_date'])
        self.fields['proposal'].initial = self._proposal
        requested_budget = number_format(self._proposal.total_budget())

        self.fields['allocated_budget'] = forms.DecimalField(localize=True)
        self.fields['allocated_budget'].help_text = f'Requested: {requested_budget} CHF'
        self.fields['allocated_budget'].label = 'Allocated budget (CHF)'

        self.helper.layout = Layout(
            Div(
                Div('proposal', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('allocated_budget', css_class='col-6'),
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
                Div('panel_recommendation', css_class='col-4'),
                Div('board_decision', css_class='col-4'),
                Div('decision_date', css_class='col-4'),
                css_class='row'
            ),
        )

    def clean(self):
        # TODO: Check proposal is eligible - else this should not be displayed anyway
        pass

    def save(self, *args, **kwargs):
        user = kwargs.pop('user')

        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        return super().save(*args, **kwargs)

    class Meta:
        model = ProposalEvaluation

        fields = ['proposal', 'allocated_budget', 'panel_remarks', 'feedback_to_applicant',
                  'panel_recommendation',
                  'board_decision', 'decision_date']
        widgets = {
            'proposal': forms.HiddenInput,
            'decision_date': XDSoftYearMonthDayPickerInput,
        }
