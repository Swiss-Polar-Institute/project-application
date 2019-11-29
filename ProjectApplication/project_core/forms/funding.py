from crispy_forms.helper import FormHelper
from dal import autocomplete
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory

from project_core.forms.utils import OrganisationNameChoiceField
from project_core.models import OrganisationName, ProposalFundingItem, Proposal


class ProposalFundingItemForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organisation_name'] = OrganisationNameChoiceField(queryset=OrganisationName.objects.all(),
                                                                       widget=autocomplete.ModelSelect2(
                                                                       url='autocomplete-organisation-names'))

        self.fields['amount'].widget.attrs['min'] = 0

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = ProposalFundingItem
        fields = ['organisation_name', 'funding_status', 'amount', 'proposal', ]
        labels = {'amount': 'Amount (CHF)'}
        localized_fields = ('amount',)


class ProposalFundingFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'bootstrap4/table_inline_formset.html'
        self.helper.form_id = 'funding_form'

    def save_fundings(self, proposal):
        for form in self.forms:
            if form.cleaned_data:
                if form.cleaned_data['DELETE'] and form.cleaned_data['id']:
                    proposal_item = form.cleaned_data['id']
                    proposal_item.delete()
                elif form.cleaned_data['DELETE'] is False:
                    proposal_item = form.save(commit=False)
                    proposal_item.proposal = proposal
                    proposal_item.save()


ProposalFundingItemFormSet = inlineformset_factory(
    Proposal, ProposalFundingItem, form=ProposalFundingItemForm, formset=ProposalFundingFormSet, extra=1,
    can_delete=True)
