from crispy_forms.helper import FormHelper
from django import forms
from django.urls import reverse

from ..models import FundingInstrument


class FundingInstrumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.fields[
            'short_name'].help_text = f'Select a funding instrument acronym. This needs to be a financial key. Please <a href="{reverse("logged-financial-key-list")}">create one if needed</a>'

    class Meta:
        model = FundingInstrument
        fields = ['long_name', 'short_name', 'description']
