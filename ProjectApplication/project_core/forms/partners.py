from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.db import transaction
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory

from project_core.forms.utils import get_field_information, LabelAndOrderNameChoiceField
from project_core.models import ProposalPartner, Proposal, PersonPosition, PhysicalPerson, PersonTitle, CareerStage
from variable_templates.utils import apply_templates
from .utils import organisations_name_autocomplete
from ..utils.orcid import field_set_read_only, orcid_div
from ..utils.utils import create_person_position


class ProposalPartnerItemForm(ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    person__physical_person__orcid = forms.CharField(
        **get_field_information(PhysicalPerson, 'orcid',
                                required=True,
                                help_text='Enter the partner\'s ORCID iD (e.g. 0000-0002-1825-0097).<br>'
                                          'Please ask the partner to create an <a href="https://orcid.org">ORCID iD</a> if they do not already have one'),
        label='ORCID iD')

    person__physical_person__first_name = forms.CharField(
        **get_field_information(PhysicalPerson, 'first_name', help_text=''),
        label='First name(s)')
    person__physical_person__surname = forms.CharField(**get_field_information(PhysicalPerson, 'surname', help_text=''),
                                                       label='Surname(s)')
    person__academic_title = forms.ModelChoiceField(PersonTitle.objects.all().order_by('title'), label='Academic title')
    person__career_stage = forms.ModelChoiceField(CareerStage.objects.all().order_by('name'), label='Career stage')
    person__group = forms.CharField(**get_field_information(PersonPosition, 'group', label='Group / lab',
                                                            help_text='Please type the names of the group(s) or laboratories to which the partner belongs for the purposes of this proposal'))

    def __init__(self, *args, **kwargs):
        call = kwargs.pop('call')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        person__organisations_initial = None

        field_set_read_only(
            [self.fields['person__physical_person__first_name'], self.fields['person__physical_person__surname']])

        if self.instance.pk:
            self.fields['id'] = self.instance.id

            self.fields['person__group'].initial = self.instance.person.group
            self.fields['person__career_stage'].initial = self.instance.person.career_stage
            self.fields['person__academic_title'].initial = self.instance.person.academic_title
            self.fields['person__physical_person__orcid'].initial = self.instance.person.person.orcid
            self.fields['person__physical_person__first_name'].initial = self.instance.person.person.first_name
            self.fields['person__physical_person__surname'].initial = self.instance.person.person.surname
            person__organisations_initial = self.instance.person.organisation_names.all()

        self.fields['person__organisations'] = organisations_name_autocomplete(initial=person__organisations_initial,
                                                                               help_text='Please select the organisation(s) to which the partner is affiliated for the purposes of this proposal.')

        apply_templates(self.fields, call)

        self.helper.layout = Layout(
            orcid_div('person__physical_person__orcid'),
            Div(
                Div('id', hidden=True),
                Div('person__physical_person__first_name', css_class='col-4'),
                Div('person__physical_person__surname', css_class='col-4'),
                Div('person__academic_title', css_class='col-2'),
                Div('person__career_stage', css_class='col-2'),
                css_class='row'
            ),
            Div(
                Div('person__organisations', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('person__group', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('role', css_class='col-12'),
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
            Div(
                Div(Field('DELETE'), css_class='col-12'),
                css_class='row'
            ),
        )

    def save_partner(self, proposal):
        cd = self.cleaned_data

        person_position = create_person_position(cd['person__physical_person__orcid'],
                                                 cd['person__physical_person__first_name'],
                                                 cd['person__physical_person__surname'],
                                                 academic_title=cd['person__academic_title'],
                                                 group=cd['person__group'],
                                                 career_stage=cd['person__career_stage'],
                                                 organisation_names=cd['person__organisations'])

        proposal_partner, created = ProposalPartner.objects.get_or_create(person=person_position,
                                                                          role=cd['role'],
                                                                          role_description=cd['role_description'],
                                                                          competences=cd['competences'],
                                                                          proposal=proposal)

        return proposal_partner

    class Meta:
        model = ProposalPartner
        fields = ['role_description', 'competences', 'role', ]
        field_classes = {'role': LabelAndOrderNameChoiceField}
        help_texts = {'role': 'Select the role of the partner in the proposed {{ activity }}'}


class ProposalPartnersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'proposal_partners_form'

    def clean(self):
        super().clean()

        if not hasattr(self, 'cleaned_data'):
            return

        orcids = set()

        for form_data in self.cleaned_data:
            if not form_data:
                continue

            partner_orcid = form_data['person__physical_person__orcid']

            if partner_orcid in orcids:
                raise forms.ValidationError('There is a duplicated partner')

            orcids.add(partner_orcid)

    @staticmethod
    def _delete_proposal_partner(proposal_partner):
        if proposal_partner is None:
            return

        proposal_partner.delete()

    def save_partners(self, proposal):
        with transaction.atomic():
            for form in self.forms:
                if form.cleaned_data:
                    if form.cleaned_data['DELETE'] and form.cleaned_data['id']:
                        ProposalPartnersFormSet._delete_proposal_partner(form.cleaned_data['id'])

                    elif form.cleaned_data['DELETE'] is False:
                        previous_proposal_partner = form.cleaned_data['id'].id if form.cleaned_data['id'] else None
                        new_proposal_partner = form.save_partner(proposal)

                        if previous_proposal_partner != new_proposal_partner.id:
                            ProposalPartnersFormSet._delete_proposal_partner(form.cleaned_data['id'])


ProposalPartnersInlineFormSet = inlineformset_factory(
    Proposal, ProposalPartner, form=ProposalPartnerItemForm, formset=ProposalPartnersFormSet, extra=1,
    can_delete=True)
