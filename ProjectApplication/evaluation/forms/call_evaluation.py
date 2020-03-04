from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.urls import reverse

from ProjectApplication import settings
from evaluation.models import CallEvaluation
from project_core.utils import user_is_in_group_name
from project_core.widgets import XDSoftYearMonthDayPickerInput


class CallEvaluationForm(forms.ModelForm):
    FORM_NAME = 'call_evaluation_form'

    def __init__(self, *args, **kwargs):
        call = kwargs.pop('call', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        if self.instance.id:
            self.helper.form_action = reverse('logged-call-evaluation-update', kwargs={'id': self.instance.id})
            self.fields['call'].initial = self.instance.call
        else:
            self.helper.form_action = reverse('logged-call-evaluation-add')+f'?call={call.id}'
            self.fields['call'].initial = call

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['panel_date'])

        self.helper.layout = Layout(
            Div(
                Div('call', css_class='col-12', hidden=True),
                css_class='row'
            ),
            Div(
                Div('panel_date', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('evaluation_sheet', css_class='col-12'),
                css_class='row'
            )
        )

    def clean(self):
        super().clean()

    def save_call_evaluation(self, user, *args, **kwargs):
        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionError()

        return super().save(*args, **kwargs)

    class Meta:
        model = CallEvaluation

        fields = ['call', 'panel_date', 'evaluation_sheet']

        widgets = {
            'panel_date': XDSoftYearMonthDayPickerInput
        }
