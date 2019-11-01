from crispy_forms.helper import FormHelper
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory

from project_core.models import ProposalPartner, Proposal


class ProposalPartnerItemForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = ProposalPartner
        fields = ['role_description', 'competences', ]


class ProposalPartnersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'bootstrap4/table_inline_formset.html'
        self.helper.form_id = 'proposal_partners_form'


ProposalPartnersInlineFormSet = inlineformset_factory(
    Proposal, ProposalPartner, form=ProposalPartnerItemForm, formset=ProposalPartnersFormSet, extra=1,
    can_delete=True)