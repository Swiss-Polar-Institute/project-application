from django import forms
from django.forms import ModelForm
from crispy_forms.layout import Layout, Div
from ..widgets import DatePickerWidget

from ..models import Proposal

from crispy_forms.helper import FormHelper
from dal import autocomplete


class ProposalForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
        else:
            self.fields['call_id'].initial = self._call.id

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.fields['duration_months'].widget.attrs['min'] = 0

        self.helper.layout = Layout(
            Div(
                Div('call_id', css_class='col-12', hidden='true'),
                Div('title', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('geographical_areas', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('keywords', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('provisional_start_date', css_class='col-4'),
                Div('provisional_end_date', css_class='col-4'),
                Div('duration_months', css_class='col-4'),
                css_class='row'
            )
        )

    def save(self, commit=True):
        self.instance.call_id = self.cleaned_data['call_id']

        model = super().save(commit)

        return model

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'keywords', 'provisional_start_date',
                  'provisional_start_date', 'provisional_end_date', 'duration_months']

        widgets = {'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords'),
                   'geographical_areas': forms.CheckboxSelectMultiple,
                   'provisional_start_date': DatePickerWidget,
                   'provisional_end_date': DatePickerWidget
                   }