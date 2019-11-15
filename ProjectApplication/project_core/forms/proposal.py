from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from dal import autocomplete
from django import forms
from django.forms import ModelForm

from ..models import Proposal, ProposalStatus
from ..widgets import DatePickerWidget


class ProposalForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
        else:
            self.fields['call_id'].initial = self._call.id

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.fields['duration_months'].widget.attrs['min'] = 0

        divs = []
        divs.append(
            Div(
                Div('call_id', css_class='col-12', hidden='true'),
                Div('title', css_class='col-12'),
                css_class='row'
            )
        )

        if self._user.is_staff:
            self.fields['proposal_status'] = forms.ModelChoiceField(ProposalStatus.objects.all().order_by('name'),
                                                                    initial=self.instance.proposal_status)
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
                Div('keywords', css_class='col-12'),
                css_class='row'
            )
        )

        divs.append(
            Div(
                Div('provisional_start_date', css_class='col-4'),
                Div('provisional_end_date', css_class='col-4'),
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

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'keywords', 'provisional_start_date',
                  'provisional_end_date', 'duration_months', ]

        widgets = {'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords'),
                   'geographical_areas': forms.CheckboxSelectMultiple,
                   'provisional_start_date': DatePickerWidget,
                   'provisional_end_date': DatePickerWidget
                   }
