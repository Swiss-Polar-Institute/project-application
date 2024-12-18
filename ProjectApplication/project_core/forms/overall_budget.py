from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.forms import ModelForm

from ..models import Proposal, Call
from ..fields import FlexibleDecimalField  # Assuming this is a custom field


class OverallBudgetForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    overall_budget = FlexibleDecimalField(
        required=False,
        help_text='Approximate budget as detailed in programme description including the 5% opportunity fund.',
        label='Requested overall budget (CHF)',
        widget=forms.TextInput(attrs={'class': 'custom-overall-budget-class'})
    )

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super().__init__(*args, **kwargs)

        # Initialize FormHelper
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('overall_budget', css_class='col-6'),
                css_class='row'
            )
        )

        if self._call is None:
            self._call = self.instance.call

        # Remove the `overall_budget` field if the question is not enabled
        if not self._call.overall_budget_question:
            self.fields.pop('overall_budget', None)
        else:
            # Add to the layout only if the field exists
            self.helper.layout = Layout(
                Div(
                    Div('overall_budget', css_class='col-6'),
                    css_class='row'
                )
            )

        # Set initial values for fields
        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
            if 'overall_budget' in self.fields:
                self.fields['overall_budget'].initial = self.instance.overall_budget
            call = self._call = self.instance.call
        else:
            self.fields['call_id'].initial = self._call.id
            call = Call.objects.get(id=self._call.id)


    def clean(self):
        super().clean()

    def save(self, commit=True):
        return super().save(commit=commit)

    class Meta:
        model = Proposal
        fields = ['overall_budget']
