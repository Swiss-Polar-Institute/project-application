from crispy_forms.helper import FormHelper
from django import forms

from ..models import FundingInstrument


class FundingInstrumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = FundingInstrument
        fields = ['long_name', 'short_name', 'description']
