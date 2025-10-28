from crispy_forms.helper import FormHelper
from dal import autocomplete
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory

from project_core.forms.utils import OrganisationNameChoiceField
from project_core.models import OrganisationName, ProposalFundingItem, Proposal


class ProposalFundingItemForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['organisation_name'].widget = autocomplete.ModelSelect2(url='autocomplete-organisation-names')
        self.fields['organisation_name'].queryset = OrganisationName.objects.all()
        self.fields['organisation_name'].required = False

        self.fields['funding_status'].required = False
        self.fields['amount'].widget.attrs['min'] = 0
        self.fields['amount'].required = False

        if 'amount' in self.initial and self.initial['amount'] is None:
            self.initial['amount'] = 0

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = ProposalFundingItem
        fields = ['organisation_name', 'funding_status', 'amount']
        labels = {'amount': 'Total (CHF)'}
        localized_fields = ('amount',)
        help_texts = {
            'amount': '',
            'organisation_name': 'Please select the organisation from which funding has been sought.<br> If it is not available amongst the options provided, type the full name and click on “Create”'
        }


class ProposalFundingFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'bootstrap4/table_inline_formset.html'
        self.helper.form_id = 'funding_form'

    def save_fundings(self, proposal):
        for form in self.forms:
            if not form.cleaned_data:
                continue  # skip unsubmitted rows

            if form.cleaned_data.get('DELETE', False) and form.cleaned_data.get('id'):
                form.cleaned_data['id'].delete()
                continue

            # skip blank rows
            if not form.cleaned_data.get('organisation_name') and not form.cleaned_data.get('amount'):
                continue

            # default value for amount
            if form.cleaned_data.get('amount') is None:
                form.cleaned_data['amount'] = 0

            proposal_item = form.save(commit=False)
            proposal_item.proposal = proposal
            proposal_item.save()


ProposalFundingItemFormSet = inlineformset_factory(
    Proposal, ProposalFundingItem, form=ProposalFundingItemForm, formset=ProposalFundingFormSet, extra=1,
    can_delete=True)
