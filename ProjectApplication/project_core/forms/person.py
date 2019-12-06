from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.forms import Form

from project_core.models import PersonTitle, Gender, PhysicalPerson, PersonPosition, Contact, CareerStage
from .utils import organisations_name_autocomplete


class PersonForm(Form):
    def __init__(self, *args, **kwargs):
        self.person_position = kwargs.pop('person_position', None)
        super().__init__(*args, **kwargs)

        first_name_initial = surname_initial = organisations_initial = group_initial = \
            academic_title_initial = email_initial = gender_initial = career_stage_initial = phd_date_initial = None

        if self.person_position:
            first_name_initial = self.person_position.person.first_name
            surname_initial = self.person_position.person.surname
            organisations_initial = self.person_position.organisation_names.all()
            group_initial = self.person_position.group
            academic_title_initial = self.person_position.academic_title
            career_stage_initial = self.person_position.career_stage
            gender_initial = self.person_position.person.gender
            email_initial = self.person_position.main_email()
            phd_date_initial = self.person_position.person.phd_date

        self.fields['academic_title'] = forms.ModelChoiceField(queryset=PersonTitle.objects.all(),
                                                               initial=academic_title_initial)

        self.fields['gender'] = forms.ModelChoiceField(queryset=Gender.objects.all(),
                                                       initial=gender_initial)

        self.fields['career_stage'] = forms.ModelChoiceField(queryset=CareerStage.objects.all(),
                                                             initial=career_stage_initial)

        self.fields['first_name'] = forms.CharField(initial=first_name_initial,
                                                    label='First name(s)')

        self.fields['surname'] = forms.CharField(initial=surname_initial,
                                                 label='Surname(s)')

        self.fields['email'] = forms.EmailField(initial=email_initial)

        self.fields['phd_date'] = forms.CharField(initial=phd_date_initial,
                                                  label='Date of PhD',
                                                  help_text='Where applicable, please enter the date on which you were awarded, or expect to be awarded your PhD (use the format mm/yyyy).',
                                                  required=False,
                                                  validators=[RegexValidator(regex='^[0-9]{4}-[0-9]{2}$',
                                                                             message='Format is yyyy-mm',
                                                                             code='Invalid format')])

        self.fields['organisation_names'] = organisations_name_autocomplete(initial=organisations_initial,
                                                                            help_text='Please select the organisation(s) to which you are affiliated for the purposes of this proposal.')

        self.fields['group'] = forms.CharField(initial=group_initial,
                                               help_text='Please type the names of the group(s) or laboratories to which you are affiliated for the purposes of this proposal',
                                               label='Group / lab',
                                               required=False)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('academic_title', css_class='col-2'),
                Div('first_name', css_class='col-4'),
                Div('surname', css_class='col-4'),
                Div('gender', css_class='col-2'),
                css_class='row'
            ),
            Div(
                Div('email', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('organisation_names', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('group', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('career_stage', css_class='col-8'),
                Div('phd_date', css_class='col-4'),
                css_class='row'
            ),
        )

    def get_person_position(self):
        """ Matches and returns the person_position from the database. """
        try:
            physical_person = PhysicalPerson.objects.get(
                first_name=self.cleaned_data['first_name'],
                surname=self.cleaned_data['surname'],
            )

            person_position = PersonPosition.objects.get(
                person=physical_person,
                academic_title=self.cleaned_data['academic_title'],
                group=self.cleaned_data['group'],
                career_stage=self.cleaned_data['career_stage']
            )

        except ObjectDoesNotExist:
            return None

        return person_position

    def save_person(self):
        if self.person_position and self.person_position.person:
            physical_person = self.person_position.person
        else:
            physical_person, created = PhysicalPerson.objects.get_or_create(
                first_name=self.cleaned_data['first_name'],
                surname=self.cleaned_data['surname'],
                defaults={
                    'gender': self.cleaned_data['gender']
                }
            )

        # Any new gender changes the previously assigned gender
        physical_person.first_name = self.cleaned_data['first_name']
        physical_person.surname = self.cleaned_data['surname']
        physical_person.gender = self.cleaned_data['gender']
        physical_person.phd_date = self.cleaned_data['phd_date']
        physical_person.save()

        if self.person_position:
            person_position = self.person_position
            person_position.person = physical_person
            person_position.academic_title = self.cleaned_data['academic_title']
            person_position.group = self.cleaned_data['group']
            person_position.career_stage = self.cleaned_data['career_stage']

            person_position.save()

        else:
            person_position, created = PersonPosition.objects.get_or_create(person=physical_person,
                                                                            academic_title=self.cleaned_data[
                                                                                'academic_title'],
                                                                            group=self.cleaned_data['group'],
                                                                            career_stage=self.cleaned_data[
                                                                                'career_stage'])

        person_position.organisation_names.set(self.cleaned_data['organisation_names'])

        try:
            email_contact = person_position.contact_set.get(method=Contact.EMAIL)
        except ObjectDoesNotExist:
            email_contact = Contact()
            email_contact.method = Contact.EMAIL
            email_contact.person_position = person_position

        email_contact.entry = self.cleaned_data['email']
        email_contact.save()

        return person_position
