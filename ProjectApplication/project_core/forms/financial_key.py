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
                Div('description', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Create Financial Key'),
                cancel_edit_button(reverse('logged-financial-key-list'))
            )
        )

    # def save(self, *args, **kwargs):
    #     user = kwargs.pop('user')
    #     instance = super().save(*args, **kwargs)
    #
    #     instance.user = user
    #     if kwargs['commit']:
    #         instance.save()
    #
    #     return instance

    class Meta:
        model = FinancialKey
        fields = ['name', 'description', ]
