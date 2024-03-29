from crispy_forms.helper import FormHelper
from django import forms
from django.db.models import Q
from django.urls import reverse

from ..models import FundingInstrument, FinancialKey


class FundingInstrumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        # funding_instrument is the Boolean field. fundinginstrument is the reverse relationship for the OneToOne
        self.fields['short_name'].queryset = FinancialKey.objects.filter(funding_instrument=True).filter(
            Q(fundinginstrument__isnull=True) | Q(fundinginstrument=self.instance))

        self.fields[
            'short_name'].help_text = f'Select a funding instrument acronym. This needs to be a financial key. Please <a href="{reverse("logged-financial-key-update")}">create one if needed</a> and refresh this page'

    class Meta:
        model = FundingInstrument
        fields = ['long_name', 'short_name', 'description']
