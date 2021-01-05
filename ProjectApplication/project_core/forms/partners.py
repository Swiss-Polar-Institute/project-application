from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.db import transaction
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory

from project_core.forms.utils import get_field_information, LabelAndOrderNameChoiceField
from project_core.models import ProposalPartner, Proposal, PersonPosition, PhysicalPerson, PersonTitle, CareerStage, \
    Role
from variable_templates.utils import apply_templates_to_fields
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
    person__career_stage = forms.ModelChoiceField(CareerStage.objects.all().order_by('list_order'),
                                                  label='Career stage')
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

        apply_templates_to_fields(self.fields, call)

        self.helper.layout = Layout(
            orcid_div('person__physical_person__orcid'),
            Div(
                Div('id', hidden=True),
                Div(Field('DELETE'), hidden=True),
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
            )
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
        self._applicant_role_description_form = kwargs.pop('applicant_role_description_form', None)
        self._applicant_person_form = kwargs.pop('person_form', None)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'proposal_partners_form'

    def clean(self):
        super().clean()

        if not hasattr(self, 'cleaned_data'):
            return

        orcids = set()

        principal_investigators_count = 0
        co_principal_investigators_count = 0

        principal_investigator = Role.objects.get(name='Principal Investigator')
        co_principal_investigator = Role.objects.get(name='Co-Principal Investigator')

        applicant_orcid = None

        if self._applicant_role_description_form.is_valid():
            applicant_role = self._applicant_role_description_form.cleaned_data['role']

            if applicant_role == principal_investigator:
                principal_investigators_count += 1
            elif applicant_role == co_principal_investigator:
                co_principal_investigators_count += 1

        if self._applicant_person_form.is_valid():
            applicant_orcid = self._applicant_person_form.cleaned_data['orcid']

        for form_data in self.cleaned_data:
            if not form_data or form_data['DELETE']:
                continue

            partner_orcid = form_data['person__physical_person__orcid']

            if partner_orcid in orcids:
                raise forms.ValidationError(
                    'A proposal partner has been entered more than once. Use the remove button to delete the duplicated partner.')

            if applicant_orcid is not None and partner_orcid == applicant_orcid:
                raise forms.ValidationError(
                    'A proposal partner has the same ORCID iD as the applicant. Please do not include the applicant as a partner.'
                )

            partner_role = form_data['role']

            if partner_role == principal_investigator:
                principal_investigators_count += 1
            elif partner_role == co_principal_investigator:
                co_principal_investigators_count += 1

            orcids.add(partner_orcid)

        if principal_investigators_count > 1:
            raise forms.ValidationError(
                'Only one person can be a Principal Investigator. If two or more people are sharing this role please enter them as Co-Principal Investigators.'
            )

        if principal_investigators_count == 0 and co_principal_investigators_count < 2:
            raise forms.ValidationError(
                'Please make sure that there is at least one Principal Investigator or at least two Co-Principal Investigators.'
            )

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
