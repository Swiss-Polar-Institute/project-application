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


class ProposalForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput())
    duration_months = FlexibleDecimalField()

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super().__init__(*args, **kwargs)

        if self._call is None:
            self._call = self.instance.call

        self._raise_duplicated_title = False

        if self._call.overall_budget_question:
            self.fields['overall_budget'] = FlexibleDecimalField(help_text='Estimate of the budget')

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
            self.fields['overall_budget'].initial = self.instance.overall_budget
            call = self._call = self.instance.call
        else:
            self.fields['call_id'].initial = self._call.id
            call = Call.objects.get(id=self._call.id)


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

    def save(self, commit=True):
        self.instance.call_id = self.cleaned_data['call_id']

        model = super().save(commit)

        return model

    def clean(self):
        cleaned_data = super().clean()

        errors = {}

        if 'overall_budget' in self.cleaned_data:
            if cleaned_data['overall_budget'] < 0:
                errors['overall_budget'] = 'Budget needs to be greater than 0'
            elif cleaned_data['overall_budget'] > self._call.budget_maximum:
                errors['overall_budget'] = f'Budget is greater than the maximum budget for this call: ' \
                                           f'{thousands_separator(self._call.budget_maximum)} CHF'

        if self._call.keywords_in_general_information_question:
            keywords_validation(errors, cleaned_data, 'keywords')

        if self._raise_duplicated_title:
            errors['title'] = forms.ValidationError(
                mark_safe('A proposal already exists with the same title and applicant for this call. '
                          'Rather than starting from scratch again please use the link with which you were provided to '
                          'edit your application. Otherwise please contact SPI '
                          '<a href="mailto:spi-grants@epfl.ch">spi-grants@epfl.ch</a> to receive a reminder of'
                          ' the link.'))

        # Converts date to datetime objects to compare with the end of the call.
        # The combine and datetime.datetime.min.time() makes it the beginning of the day
        proposal_start_date = datetime.datetime.combine(cleaned_data['start_date'], datetime.datetime.min.time())
        proposal_end_date = datetime.datetime.combine(cleaned_data['end_date'], datetime.datetime.min.time())

        proposal_start_date = utc.localize(proposal_start_date)
        proposal_end_date = utc.localize(proposal_end_date)

        call_submission_deadline = self._call.submission_deadline

        if proposal_end_date < proposal_start_date:
            errors['start_date'] = forms.ValidationError('Proposal start date needs to be before end date')

        if proposal_end_date < call_submission_deadline:
            errors['end_date'] = forms.ValidationError(
                'Proposal end date needs to be after call submission deadline')

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def raise_duplicated_title(self):
        self._raise_duplicated_title = True
        self.full_clean()

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
            'location': 'Name of more precise location of where the proposed {{ activity }} would take place (not coordinates)',
            'keywords': 'Please select at least 5 keywords that describe the proposed {{ activity }}. If the keywords you are looking for do not exist, then add each term separately',
            'start_date': 'Date on which the {{ activity }} to be funded by SPI, is expected to start',
            'end_date': 'Date on which the {{ activity }} to be funded by SPI, is expected to end',
        }

        labels = {'location': 'Precise region',
                  'geographical_areas': 'Geographical focus'}
