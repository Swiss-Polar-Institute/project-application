from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse

from ProjectApplication import settings
from evaluation.models import CallEvaluation, Reviewer
from evaluation.utils import ReviewerMultipleChoiceField
from project_core.forms.utils import cancel_edit_button
from project_core.utils.utils import user_is_in_group_name
from project_core.widgets import XDSoftYearMonthDayPickerInput


class CallEvaluationForm(forms.ModelForm):
    FORM_NAME = 'call_evaluation_form'

    def __init__(self, *args, **kwargs):
        call = kwargs.pop('call', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        if self.instance.id:
            self.helper.form_action = reverse('logged-call-evaluation-update', kwargs={'pk': self.instance.id})
            self.fields['call'].initial = call = self.instance.call
        else:
            self.helper.form_action = reverse('logged-call-evaluation-add') + f'?call={call.id}'
            self.fields['call'].initial = call

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['panel_date'])

        if hasattr(call, 'callevaluation'):
            cancel_edit_url = reverse('logged-call-evaluation-detail', kwargs={'pk': call.callevaluation.id})
            initial_reviewers = call.reviewer_set.all()
        else:
            cancel_edit_url = reverse('logged-call-evaluation-add') + f'?call={call.id}'
            initial_reviewers = []

        self.fields['reviewers'] = ReviewerMultipleChoiceField(initial=initial_reviewers,
                                                               queryset=Reviewer.objects.all(),
                                                               required=True,
                                                               widget=FilteredSelectMultiple(
                                                                   is_stacked=True,
                                                                   verbose_name='reviewers'),
                                                               help_text=self.Meta.help_texts['reviewers'])

        self.helper.layout = Layout(
            Div(
                Div('call', css_class='col-12', hidden=True),
                css_class='row'
            ),
            Div(
                Div('reviewers', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('panel_date', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('post_panel_management_table', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Call Evaluation'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    def clean(self):
        super().clean()

    def save_call_evaluation(self, user, *args, **kwargs):
        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionError()

        reviewers = self.cleaned_data['reviewers']

        call_evaluation = super().save(*args, **kwargs)

        call_evaluation.call.reviewer_set.set(reviewers)

        return call_evaluation

    class Meta:
        model = CallEvaluation

        fields = ['call', 'panel_date', 'post_panel_management_table']

        help_texts = {
            'reviewers': 'Select the reviewers that you would like to be added for this call. This is everyone that '
                         'will review individual proposals and be on the review panel. If you cannot find the person '
                         'you are looking for, please contact Carles to add them. This is not currently possible as a '
                         'management user.'
        }

        widgets = {
            'panel_date': XDSoftYearMonthDayPickerInput
        }
