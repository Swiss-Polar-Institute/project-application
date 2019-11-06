from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory

from project_core.forms.utils import get_field_information
from project_core.models import ProposalPartner, Proposal, PersonPosition, PhysicalPerson, PersonTitle, Role


class RoleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, role: Role):
        return role.short()


class ProposalPartnerItemForm(ModelForm):
    person__physical_person__first_name = forms.CharField(**get_field_information(PhysicalPerson, 'first_name'))
    person__physical_person__surname = forms.CharField(**get_field_information(PhysicalPerson, 'surname'))
    person__academic_title = forms.ModelChoiceField(PersonTitle.objects.all().order_by('title'))

    # person__physical_person__gender =
    person__group = forms.CharField(help_text=PersonPosition._meta.get_field('group').help_text,
                                    max_length=PersonPosition._meta.get_field('group').max_length,
                                    required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        initial_role = None

        self.fields['id'] = None

        if self.instance.pk:
            self.fields['person__group'].initial = self.instance.person.group
            self.fields['person__academic_title'].initial = self.instance.person.academic_title
            self.fields['person__physical_person__first_name'].initial = self.instance.person.person.first_name
            self.fields['person__physical_person__surname'].initial = self.instance.person.person.surname
            self.fields['id'] = self.instance.pk
            initial_role = self.instance.role

        self.fields['person__academic_title'].label = 'Academic title'
        self.fields['person__physical_person__first_name'].label = 'First name'
        self.fields['person__physical_person__surname'].label = 'Surname'
        self.fields['person__group'].label = 'Group'

        self.fields['role'] = RoleChoiceField(queryset=Role.objects.all().order_by('name'), initial=initial_role)

        self.helper.layout = Layout(
            Div(
                Div('id', hidden=True),
                Div('person__academic_title', css_class='col-2'),
                Div('person__physical_person__first_name', css_class='col-5'),
                Div('person__physical_person__surname', css_class='col-5'),
                css_class='row'
            ),
            Div(
                Div('person__group', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('career_stage', css_class='col-12'),
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

    def save(self, commit=True):
        proposal_partner = super().save(commit=False)

        person__group = self.cleaned_data['person__group']
        person__academic_title = self.cleaned_data['person__academic_title']

        person__physical_person__first_name = self.cleaned_data['person__physical_person__first_name']
        person__physical_person__surname = self.cleaned_data['person__physical_person__surname']

        if self.instance.id:
            # Needs to update and existing partner
            person = self.instance.person
            assert person

            person.group = person__group
            person.academic_title = person__academic_title
            person.save()

            person__physical_person = self.instance.person.person
            assert person__physical_person

            person__physical_person.first_name = person__physical_person__first_name
            person__physical_person.surname = person__physical_person__surname
            person__physical_person.save()

            return proposal_partner

        else:
            # Needs to create a partner
            physical_person, created = PhysicalPerson.objects.get_or_create(
                first_name=person__physical_person__first_name,
                surname=person__physical_person__surname)

            person_position, created = PersonPosition.objects.get_or_create(
                person=physical_person,
                academic_title=person__academic_title,
                group=person__group
            )

            proposal_partner.person = person_position

        if commit:
            proposal_partner.save()

        return proposal_partner

    class Meta:
        model = ProposalPartner
        fields = ['role_description', 'competences', 'career_stage', 'role', ]


class ProposalPartnersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'proposal_partners_form'

    def clean(self):
        super().clean()

        sets_of_person_role_proposal = set()

        for form_data in self.cleaned_data:
            # len(form_data) because the form without any values arrive here
            if len(form_data) != 0 and form_data['id'] is None:
                # On the ProposalPartnerItemForm.save() it will PhysicalPerson.get_or_create
                # and PersonPosition.get_or_create .
                # The result can be that the ProposalPartner unique_together:
                # (person, role, proposal) might be duplicated
                # Here we will raise a ValidationError if this is going to be the case

                # Updating a partner - no problems should happen regaring ins
                proposal_partner = None
                try:
                    physical_person = PhysicalPerson.objects.get(
                        first_name=form_data['person__physical_person__first_name'],
                        surname=form_data['person__physical_person__surname'])

                    person_position = PersonPosition.objects.get(
                        person=physical_person,
                        academic_title=form_data['person__academic_title'],
                        group=form_data['person__group']
                    )

                    proposal_partner = ProposalPartner.objects.get(
                        person=person_position, role=form_data['role'], proposal=self.instance)

                    raise forms.ValidationError('There is a duplicated partner')

                except ObjectDoesNotExist:
                    instance_id = self.instance.id if self.instance else None
                    new_set = (proposal_partner, form_data['role'].id, instance_id)
                    if new_set in sets_of_person_role_proposal:
                        raise forms.ValidationError('There is a duplicated partner')

                    sets_of_person_role_proposal.add(new_set)

    def save_partners(self, proposal):
        for form in self.forms:
            if form.cleaned_data:
                if form.cleaned_data['DELETE'] and form.cleaned_data['id']:
                    partner = form.cleaned_data['id']
                    partner.delete()
                elif form.cleaned_data['DELETE'] is False:
                    partner = form.save(commit=False)
                    partner.proposal = proposal
                    partner.save()


ProposalPartnersInlineFormSet = inlineformset_factory(
    Proposal, ProposalPartner, form=ProposalPartnerItemForm, formset=ProposalPartnersFormSet, extra=1,
    can_delete=True)
