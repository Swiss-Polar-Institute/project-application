from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory
from django import forms

from project_core.models import ProposalPartner, Proposal, PersonPosition, PhysicalPerson


def get_model_information(model, field, information):
    return getattr(model._meta.get_field(field), information)


def get_field_information(model, field):
    kwargs = {}

    kwargs['help_text'] = get_model_information(model, field, 'help_text')
    kwargs['required'] = not get_model_information(model, field, 'blank')

    max_length = get_model_information(model, field, 'max_length')
    if max_length is not None:
        kwargs['max_length'] = max_length

    return kwargs


class ProposalPartnerItemForm(ModelForm):
    person__physical_person__first_name = forms.CharField(**get_field_information(PhysicalPerson, 'first_name'))
    person__physical_person__surname = forms.CharField(**get_field_information(PhysicalPerson, 'surname'))

    # person__physical_person__gender =
    person__group = forms.CharField(help_text=PersonPosition._meta.get_field('group').help_text,
                                    max_length=PersonPosition._meta.get_field('group').max_length,
                                    required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        if self.instance.pk:
            self.fields['person__group'].initial = self.instance.person.group

        self.helper.layout = Layout(
            Div(
                Div('person__physical_person__first_name', css_class='col-6'),
                Div('person__physical_person__surname', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('role_description', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('competences', css_class='col-12'),
                css_class='row'
            ),
        )

    def save(self, commit=True):
        proposal_partner = super().save(commit=False)
        person__group = self.cleaned_data['person__group']

        if person__group:
            if proposal_partner.person:
                proposal_partner.person.group = person__group

            else:
                proposal_partner.person = PersonPosition.objects.create(group=person__group)

        if commit:
            proposal_partner.save()

        return proposal_partner

    class Meta:
        model = ProposalPartner
        fields = ['role_description', 'competences', ]


class ProposalPartnersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'proposal_partners_form'


ProposalPartnersInlineFormSet = inlineformset_factory(
    Proposal, ProposalPartner, form=ProposalPartnerItemForm, formset=ProposalPartnersFormSet, extra=1,
    can_delete=True)
