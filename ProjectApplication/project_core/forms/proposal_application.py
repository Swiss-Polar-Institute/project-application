import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.timezone import utc

from variable_templates.utils import apply_templates_to_fields
from .utils import keywords_validation
from ..fields import FlexibleDecimalField
from ..models import Proposal, Call
from ..templatetags.thousands_separator import thousands_separator
from ..widgets import XDSoftYearMonthDayPickerInput
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class ProposalApplicationForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    duration_months = FlexibleDecimalField(required=False)

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super().__init__(*args, **kwargs)
        # self.fields['keywords'].required = True
        # self.fields['geographical_areas'].required = True

        for field_name, field in self.fields.items():
            if field_name != 'location':
                field.widget.attrs.update({'class': 'required_field'})
            field.required = False

        if self._call is None:
            self._call = self.instance.call

        self._raise_duplicated_title = False

        if self._call.overall_budget_question:
            self.fields['overall_budget'] = FlexibleDecimalField(help_text='Please report the total budget figure. A detailed budget should be uploaded in the following section, adhering to the structure in the respective template. For further information on eligible costs, please refer to the call text.', label='Requested overall budget (CHF)', required=False)

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
            self.fields['overall_budget'].initial = self.instance.overall_budget
            call = self._call = self.instance.call
        else:
            self.fields['call_id'].initial = self._call.id
            call = Call.objects.get(id=self._call.id)

        if self._call and self._call.funding_instrument:
            funding_long_name = self._call.funding_instrument.long_name
            print(f"Funding Instrument: {funding_long_name}")  # For debugging

            if funding_long_name == "CASCADES Expedition":
                self.fields['geographical_areas'].help_text = "For a CASCADES expedition proposal, choose the Arctic."
                self.fields['location'].help_text = "State which leg(s) are relevant to the proposed project."
            if funding_long_name == "SPI Forel Grants":
                self.fields['geographical_areas'].help_text = "For a proposal on the Forel, choose the Artic."
                self.fields['location'].help_text = "State which leg(s) are relevant to the proposed project."

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['start_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['end_date'])

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.fields['duration_months'].help_text = 'Expected duration of the {{ activity }} in months'
        apply_templates_to_fields(self.fields, call)

        divs = []
        divs.append(
            Div(
                Div('call_id', css_class='col-12', hidden='true'),
                Div('title', css_class='col-12'),
                css_class='row'
            )
        )

        divs.append(
            Div(
                Div('geographical_areas', css_class='col-12'),
                css_class='row'
            )
        )
        divs.append(
            Div(
                Div('location', css_class='col-12'),
                css_class='row'
            )
        )

        if call.keywords_in_general_information_question:
            divs.append(
                Div(
                    Div('keywords', css_class='col-12'),
                    css_class='row'
                )
            )

        divs.append(
            Div(
                Div('start_date', css_class='col-4'),
                Div('end_date', css_class='col-4'),
                Div('duration_months', css_class='col-4'),
                css_class='row'
            )
        )

        if call.overall_budget_question:
            divs.append(
                Div(
                    Div('overall_budget', css_class='col-4'),
                    css_class='row'
                )
            )
        self.helper.layout = Layout(*divs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        # Validate form data
        if not self.is_valid():
            raise ValidationError("The data provided did not pass validation.")
        self.instance.call_id = self.cleaned_data.get('call_id')
        model = super().save(commit)
        return model

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'location', 'keywords', 'start_date',
                  'end_date', 'duration_months', 'overall_budget']

        widgets = {'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords'),
                   'geographical_areas': forms.CheckboxSelectMultiple,
                   'start_date': XDSoftYearMonthDayPickerInput,
                   'end_date': XDSoftYearMonthDayPickerInput,
                   }

        help_texts = {
            'geographical_areas': 'Select all options describing the geographical focus of this {{ activity }}',
            'title': 'Name of the proposed {{ activity }}',
            'location': 'More precise location of the proposed {{ activity }} (not coordinates)',
            'keywords': 'Please select at least 5 keywords that describe the proposed {{ activity }}. If the keywords you are looking for do not exist, then add each term separately',
            'start_date': 'Date on which the {{ activity }} to be funded by SPI, is expected to start',
            'end_date': 'Date on which the {{ activity }} to be funded by SPI, is expected to end',
        }

        labels = {'location': 'Precise region'}