from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from grant_management.models import LaySummary
from project_core.forms.utils import cancel_edit_button
from project_core.widgets import XDSoftYearMonthDayPickerInput


class LaySummaryModelForm(forms.ModelForm):
    FORM_NAME = 'lay_summary'

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)

        try:
            instance = LaySummary.objects.get(project=project)
        except ObjectDoesNotExist:
            instance = None

        super().__init__(*args, instance=instance, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])

        cancel_edit_url = reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})

        self.fields['project'].initial = project

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Div(
                Div('project', css_class='col-6', hidden=True),
                css_class='row'
            ),
            Div(
                Div('due_date', css_class='col-4'),
                Div('sent_date', css_class='col-4'),
                Div('reception_date', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('text', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('author', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('web_version', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Deliverables'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    class Meta:
        model = LaySummary
        fields = ['project', 'due_date', 'sent_date', 'reception_date', 'text', 'author', 'web_version']
        labels = {'text': 'Lay summary'}
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput
        }
