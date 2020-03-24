from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML
from django import forms
from django.forms import ModelForm

from project_core.forms.utils import get_field_information, organisations_name_autocomplete
from project_core.models import ExternalProject
from project_core.models import PersonPosition, PhysicalPerson, PersonTitle
from project_core.utils.orcid import field_set_read_only, orcid_div


class PersonPositionMixin:
    def __init__(self):
        pass

    def _add_person_fields(self):
        self.fields['person__physical_person__orcid'] = forms.CharField(initial='', label='ORCID iD', max_length=19,
                                                                        help_text='Please enter your ORCID iD and press the button. If you do not have one please create one at <a href="https://orcid.org/">ORCID</a>')

        self.fields['person__physical_person__first_name'] = forms.CharField(
            **get_field_information(PhysicalPerson, 'first_name', help_text=''),
            label='First name(s)')
        self.fields['person__physical_person__surname'] = forms.CharField(
            **get_field_information(PhysicalPerson, 'surname', help_text=''),
            label='Surname(s)')

        field_set_read_only(
            [self.fields['person__physical_person__first_name'], self.fields['person__physical_person__surname']])

        self.fields['person__academic_title'] = forms.ModelChoiceField(PersonTitle.objects.all().order_by('title'),
                                                                       label='Academic title', )
        self.fields['person__organisations'] = organisations_name_autocomplete(initial=None,
                                                                               help_text='Please select the organisation(s) to which the supervisor belongs.')
        self.fields['person__group'] = forms.CharField(
            **get_field_information(PersonPosition, 'group', label='Group / lab',
                                    help_text='Please type the names of the group(s) or laboratories to which the overarching project supervisor belongs.'))

    def _set_person(self, person):
        if person:
            self.fields['person__group'].initial = person.group
            self.fields['person__academic_title'].initial = person.academic_title
            self.fields['person__physical_person__orcid'].initial = person.person.orcid
            self.fields['person__physical_person__first_name'].initial = person.person.first_name
            self.fields['person__physical_person__surname'].initial = person.person.surname
            self.fields['person__organisations'].initial = person.organisation_names.all()

    def _save_person(self, person_position):
        person__group = self.cleaned_data['person__group']
        person__academic_title = self.cleaned_data['person__academic_title']
        person__physical_person__orcid = self.cleaned_data['person__physical_person__orcid']
        person__physical_person__first_name = self.cleaned_data['person__physical_person__first_name']
        person__physical_person__surname = self.cleaned_data['person__physical_person__surname']
        person__organisations = self.cleaned_data['person__organisations']

        if person_position:
            # Needs to update and existing partner
            person_position.group = person__group
            person_position.academic_title = person__academic_title
            person_position.organisation_names.set(person__organisations)
            # Updates only the fields that might have been updated. See below the explanation for
            # person__physical_person.save(update_fields)

            # Note that organisation_names is saved (even not in update_fields) since it's a many-to-many
            person_position.save(update_fields=['group', 'academic_title'])

            person__physical_person = person_position.person
            assert person__physical_person

            person__physical_person.first_name = person__physical_person__first_name
            person__physical_person.surname = person__physical_person__surname
            person__physical_person.orcid = person__physical_person__orcid

            # update_fields is required because only first_name and surname can have changed from this form
            # The problem that this solve is that: if the applicant is the same as the overarching project supervisor
            # and the applicant was updating the PhD date of the applicant: the PhD date was updated twice in the database:
            # the new PhD date and then when saving the overarching project it was reverting to the previous date
            person__physical_person.save(update_fields=['first_name', 'surname', 'orcid'])

            return person_position

        else:
            # Needs to create a partner
            physical_person, created = PhysicalPerson.objects.get_or_create(
                first_name=person__physical_person__first_name,
                surname=person__physical_person__surname)

            person_position, created = PersonPosition.objects.get_or_create(
                person=physical_person,
                academic_title=person__academic_title,
                group=person__group,
                career_stage=None
            )

            person_position.organisation_names.set(person__organisations)

            return person_position

    def _person_layout(self, description):
        return [
            Div(
                Div(
                    HTML(description), css_class='col-12'),
                css_class='row'),
            orcid_div('person__physical_person__orcid'),
            Div(
                Div('person__physical_person__first_name', css_class='col-4'),
                Div('person__physical_person__surname', css_class='col-4'),
                Div('person__academic_title', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('person__organisations', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('person__group', css_class='col-12'),
                css_class='row'
            )
        ]


class ProjectOverarchingForm(ModelForm, PersonPositionMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self._add_person_fields()

        if self.instance:
            self._set_person(self.instance.leader)

        self.helper.layout = Layout(
            Div(
                Div('id', hidden=True),
                Div('title')
            ),
            *self._person_layout('Please add the details of the overarching project supervisor.')
        )

    def save(self, commit=True):
        project_overarching = super().save(commit=False)

        person = self._save_person(project_overarching.leader)

        project_overarching.leader = person

        if commit:
            project_overarching.save()

        return project_overarching

    class Meta:
        model = ExternalProject
        fields = ['id', 'title', ]
