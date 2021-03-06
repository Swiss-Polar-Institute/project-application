from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML
from django import forms
from django.forms import ModelForm

from project_core.forms.utils import get_field_information, organisations_name_autocomplete
from project_core.models import ExternalProject
from project_core.models import PersonPosition, PhysicalPerson, PersonTitle
from project_core.utils.orcid import field_set_read_only, orcid_div
from project_core.utils.utils import create_person_position


class ProjectOverarchingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self._add_person_fields()

        if self.instance:
            self._set_person(self.instance.leader)

        self.helper.layout = Layout(
            Div(
                Div('title')
            ),
            *self._person_layout('Please add the details of the overarching project supervisor.')
        )

    def _add_person_fields(self):
        self.fields['person__physical_person__orcid'] = forms.CharField(**get_field_information(PhysicalPerson, 'orcid',
                                                                                                label='ORCID iD',
                                                                                                required=True,
                                                                                                help_text='Enter the supervisor\'s ORCID iD (e.g.: 0000-0002-1825-0097).<br>'
                                                                                                          'Please ask the supervisor to create an <a href="https://orcid.org">ORCID iD</a> if they do not already have one.'))

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

    def _save_leader(self):
        cd = self.cleaned_data

        person_position = create_person_position(orcid=cd['person__physical_person__orcid'],
                                                 first_name=cd['person__physical_person__first_name'],
                                                 surname=cd['person__physical_person__surname'],
                                                 academic_title=cd['person__academic_title'],
                                                 group=cd['person__group'],
                                                 organisation_names=cd['person__organisations'])
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

    def save(self, commit=True):
        project_overarching = super().save(commit=False)

        person = self._save_leader()

        project_overarching.leader = person

        if commit:
            project_overarching.save()

        return project_overarching

    class Meta:
        model = ExternalProject
        fields = ['title', ]
