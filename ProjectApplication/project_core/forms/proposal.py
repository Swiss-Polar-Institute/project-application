import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.timezone import utc

from variable_templates.utils import apply_templates
from ..models import Proposal, ProposalStatus, Call
from ..widgets import XDSoftYearMonthDayPickerInput


class ProposalForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._in_management = kwargs.pop('in_management', False)

        super().__init__(*args, **kwargs)

        self._raise_duplicated_title = False

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
            call = self._call = self.instance.call
        else:
            self.fields['call_id'].initial = self._call.id
            call = Call.objects.get(id=self._call.id)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['start_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['end_date'])

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.fields['duration_months'].widget.attrs['min'] = 0

        apply_templates(self.fields, call)

        divs = []
        divs.append(
            Div(
                Div('call_id', css_class='col-12', hidden='true'),
                Div('title', css_class='col-12'),
                css_class='row'
            )
        )

        if self._in_management:
            self.fields['proposal_status'] = forms.ModelChoiceField(ProposalStatus.objects.all().order_by('name'))

            if self.instance.id:
                self.fields['proposal_status'].initial = self.instance.proposal_status

            divs.append(
                Div(
                    Div('proposal_status', css_class='col-12'),
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

        self.helper.layout = Layout(*divs)

    def save(self, commit=True):
        self.instance.call_id = self.cleaned_data['call_id']

        if 'proposal_status' in self.cleaned_data:
            self.instance.proposal_status = self.cleaned_data['proposal_status']

        model = super().save(commit)

        return model

    def clean(self):
        super().clean()

        errors = {}

        if len(self.cleaned_data['keywords']) < 5:
            errors['keywords'] = forms.ValidationError('Please enter at least 5 keywords')

        if self._raise_duplicated_title:
            errors['title'] = forms.ValidationError(
                mark_safe('A proposal already exists with the same title and applicant for this call. '
                          'Rather than starting from scratch again please use the link with which you were provided to '
                          'edit your application. Otherwise please contact SPI '
                          '<a href="mailto:spi-grants@epfl.ch">spi-grants@epfl.ch</a> to receive a reminder of'
                          ' the link.'))

        # Converts date to datetime objects to compare with the end of the call.
        # The combine and datetime.datetime.min.time() makes it the beginning of the day
        proposal_start_date = datetime.datetime.combine(self.cleaned_data['start_date'], datetime.datetime.min.time())
        proposal_end_date = datetime.datetime.combine(self.cleaned_data['end_date'], datetime.datetime.min.time())

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

    def raise_duplicated_title(self):
        self._raise_duplicated_title = True
        self.full_clean()

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'location', 'keywords', 'start_date',
                  'end_date', 'duration_months', ]

        widgets = {'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords'),
                   'geographical_areas': forms.CheckboxSelectMultiple,
                   'start_date': XDSoftYearMonthDayPickerInput,
                   'end_date': XDSoftYearMonthDayPickerInput
                   }

        help_texts = {
            'geographical_areas': 'Select all options describing the geographical focus of this {{ activity }}',
            'title': 'Name of the proposed {{ activity }}',
            'location': 'Name of more precise location of where the proposed {{ activity }} would take place (not coordinates)',
            'keywords': 'Please select at least 5 keywords that describe the proposed {{ activity }}. If the keywords you are looking for do not exist, then add each term separately.'
                        '',
            'start_date': "Date on which the {{ activity }} to be funded by SPI, is expected to start. \
                                        If a calendar doesn't appear when clicking on this field, please enter the date in the format dd-mm-yyyy. If all else fails, please use another browser, such as Firefox",
            'end_date': "Date on which the {{ activity }} to be funded by SPI, is expected to end. \
                                        If a calendar doesn't appear when clicking on this field, please enter the date in the format dd-mm-yyyy. If all else fails, please use another browser, such as Firefox",
            'duration_months': 'Expected duration of the field trip in months'}

        labels = {'location': 'Precise region',
                  'geographical_areas': 'Geographical focus'}
