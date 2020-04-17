from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from dal import autocomplete
from django import forms
from django.urls import reverse

from grant_management.models import GrantAgreement
from project_core.forms.utils import cancel_edit_button
from project_core.widgets import XDSoftYearMonthDayPickerInput


class GrantAgreementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['signed_date'])
        self.fields['project'].initial = project.id

        self.helper = FormHelper(self)
        cancel_url = reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('signed_by', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('signed_date', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('file', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Grant Agreement'),
                cancel_edit_button(cancel_url)
            )
        )

    class Meta:
        model = GrantAgreement
        fields = ['project', 'signed_date', 'signed_by', 'file']
        widgets = {'signed_date': XDSoftYearMonthDayPickerInput,
                   'signed_by': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')}
