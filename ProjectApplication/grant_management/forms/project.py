from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse

from project_core.forms.utils import cancel_edit_button
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class ProjectBasicInformationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['start_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['end_date'])

        self.helper = FormHelper(self)
        cancel_url = reverse('logged-grant_management-project-detail', kwargs={'pk': self.instance.id})

        self.helper.layout = Layout(
            Div(
                Div('start_date', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('end_date', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Information'),
                cancel_edit_button(cancel_url)
            )
        )

    class Meta:
        model = Project
        fields = ['start_date', 'end_date']
        widgets = {'start_date': XDSoftYearMonthDayPickerInput,
                   'end_date': XDSoftYearMonthDayPickerInput
                   }
