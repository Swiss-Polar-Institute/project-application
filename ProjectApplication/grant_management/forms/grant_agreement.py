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
                Div('file', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('signed_date', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('signed_by', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Grant Agreement'),
                cancel_edit_button(cancel_url)
            )
        )

    def clean(self):
        cd = self.cleaned_data
        signed_date = cd.get('signed_date', None)
        signed_by = cd['signed_by']

        errors = {}

        if signed_date is None and signed_by.count() > 0:
            errors['signed_date'] = 'Signed date is required if the grant agreement is signed'

        if signed_by.count() == 0 and signed_date:
            errors['signed_by'] = 'Signed by is required if signed date is entered'

        if errors:
            raise forms.ValidationError(errors)
        pass

    class Meta:
        model = GrantAgreement
        fields = ['project', 'signed_date', 'signed_by', 'file']
        labels = {'file': 'Grant agreement'}
        help_texts = {
            'signed_by': 'People who signed the grant agreement. Please do not use spaces when searching, you can search by first name or surname'}
        widgets = {'signed_date': XDSoftYearMonthDayPickerInput,
                   'signed_by': autocomplete.ModelSelect2Multiple(url='logged-autocomplete-physical-people')}
