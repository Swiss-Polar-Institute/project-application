from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.urls import reverse

from .utils import cancel_edit_button
from ..models import FinancialKey


class FinancialKeyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('funding_instrument', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('description', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Create Financial Key'),
                cancel_edit_button(reverse('logged-financial-key-list'))
            )
        )

    class Meta:
        model = FinancialKey
        fields = ['name', 'description', 'funding_instrument', ]
