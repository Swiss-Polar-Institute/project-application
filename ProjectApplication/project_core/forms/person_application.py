from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, ValidationError
from django.forms import Form
from phonenumber_field.formfields import PhoneNumberField

from project_core.models import PersonTitle, Gender, PhysicalPerson, PersonPosition, Contact, CareerStage
from project_core.utils.orcid import orcid_div, field_set_read_only
from .utils import organisations_name_autocomplete, get_field_information
from ..utils.utils import create_person_position
from ..widgets import XDSoftYearMonthPickerInput

HELP_TEXTS_HEAD_OF_YOUR_RESEARCH = {'orcid': 'Enter the ORCID iD (e.g.: 0000-0002-1825-0097).<br>'
                                             'Please ask head of research unit if unknown',
                                    'first_name': 'Populated from ORCID iD',
                                    'surname': 'Populated from ORCID iD',
                                    'academic_title': 'Mandatory if ORCID iD is entered'}


class PersonApplicationForm(Form):
    def __init__(self, *args, **kwargs):
        self.person_position = kwargs.pop('person_position', None)
        self._only_basic_fields = kwargs.pop('only_basic_fields', False)
        self._all_fields_are_optional = kwargs.pop('all_fields_are_optional', True)
        help_texts = kwargs.pop('help_texts', {})
        career_stage_queryset = kwargs.pop('career_stages_queryset', None)

        super().__init__(*args, **kwargs)

        orcid_initial = first_name_initial = surname_initial = organisations_initial = group_initial = \
            academic_title_initial = email_initial = phone_initial = gender_initial = career_stage_initial = phd_date_initial = None

        if self.person_position:
            orcid_initial = self.person_position.person.orcid
            first_name_initial = self.person_position.person.first_name
            surname_initial = self.person_position.person.surname
            organisations_initial = self.person_position.organisation_names.all()
            group_initial = self.person_position.group
            academic_title_initial = self.person_position.academic_title
            career_stage_initial = self.person_position.career_stage
            gender_initial = self.person_position.person.gender
            email_initial = self.person_position.main_email()
            phone_initial = self.person_position.main_phone()

            if self.person_position.person.phd_date:
                # In the database is always saved as yyyy-mm (validator in the model) but it's visualized as mm-yyyy
                phd_date_parts = self.person_position.person.phd_date.split('-')
                phd_date_initial = f'{phd_date_parts[1]}-{phd_date_parts[0]}'

        self.fields['orcid'] = forms.CharField(initial=orcid_initial,
                                               **get_field_information(PhysicalPerson, 'orcid', label='ORCID iD',
                                                                       required=True,
                                                                       help_text='Enter your ORCID iD (e.g.: 0000-0002-1825-0097).<br>'
                                                                                 'Please create an <a href="https://orcid.org">ORCID iD</a> if you do not already have one'))

        self.fields['academic_title'] = forms.ModelChoiceField(queryset=PersonTitle.objects.all(),
                                                               initial=academic_title_initial,
                                                               required=not self._only_basic_fields)

        self.fields['first_name'] = forms.CharField(initial=first_name_initial,
                                                    label='First name(s)',
                                                    help_text='Your name is populated from your ORCID record. If you would like to change it please amend it in <a href="https://orcid.org/login">ORCID</a>')

        self.fields['surname'] = forms.CharField(initial=surname_initial,
                                                 label='Surname(s)',
                                                 help_text='Your surname is populated from your ORCID record. If you would like to change it please amend it in <a href="https://orcid.org/login">ORCID</a>')

        field_set_read_only([self.fields['first_name'], self.fields['surname']])

        if self._only_basic_fields == False:
            self.fields['gender'] = forms.ModelChoiceField(queryset=Gender.objects.all(),
                                                           initial=gender_initial)

            if career_stage_queryset is None:
                career_stage_queryset = CareerStage.objects.all().order_by('list_order', 'name')

            self.fields['career_stage'] = forms.ModelChoiceField(
                queryset=career_stage_queryset,
                initial=career_stage_initial)

            self.fields['email'] = forms.EmailField(initial=email_initial,
                                                    help_text='Please write a valid email address. You will receive a confirmation email when saving and submitting your application form. This email address will also be used for communication purposes')

            self.fields['phone'] = PhoneNumberField(initial=phone_initial,
                                                    help_text='Phone number e.g.: +41222222222 . Extension can be added with xNN at the end')

            self.fields['phd_date'] = forms.CharField(initial=phd_date_initial,
                                                      label='Date of PhD',
                                                      help_text='Where applicable, please enter the date on which you were awarded, or expect to be awarded your PhD (use the format mm-yyyy)',
                                                      required=False,
                                                      widget=XDSoftYearMonthPickerInput,
                                                      validators=[RegexValidator(regex='^[0-9]{2}-[0-9]{4}$',
                                                                                 message='Format is mm-yyyy',
                                                                                 code='Invalid format')])

            self.fields['organisation_names'] = organisations_name_autocomplete(initial=organisations_initial,
                                                                                help_text='Please select the organisation(s) to which you are affiliated for the purposes of this proposal.')

            self.fields['group'] = forms.CharField(initial=group_initial,
                                                   help_text='Please type the names of the group(s) or laboratories to which you are affiliated for the purposes of this proposal',
                                                   label='Group / lab',
                                                   required=False)

            # If adding fields here: see below to remove them from the self.helper.layout

        used_help_texts = []
        for field_str, field in self.fields.items():
            if self._all_fields_are_optional:
                field.required = False

            if field_str in help_texts:
                self.fields[field_str].help_text = help_texts[field_str]
                used_help_texts.append(field_str)

        if len(used_help_texts) != len(help_texts):
            print('Unused help texts:', help_texts.keys() - used_help_texts)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            orcid_div('orcid'),
            Div(
                Div('first_name', css_class='col-4'),
                Div('surname', css_class='col-4'),
                Div('academic_title', css_class='col-2'),
                Div('gender', css_class='col-2'),
                css_class='row'
            ),
            Div(
                Div('career_stage', css_class='col-8'),
                Div('phd_date', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('email', css_class='col-6'),
                Div('phone', css_class='col-6'),
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
        )

        if self._only_basic_fields:
            # The Layout always includes all the fields. Now it's better to remove the fields that don't exist
            # to avoid django-crispy-forms warnings (not fatal)
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'gender')
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'career_stage')
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'email')
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'phone')
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'phd_date')
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'organisation_names')
            PersonForm._delete_field_from_layout(self.helper.layout.fields, 'group')

    @staticmethod
    def _delete_field_from_layout(container, field_str):
        for item in container:
            if type(item) == Div:
                PersonForm._delete_field_from_layout(item, field_str)
            elif type(item) == str and item == field_str:
                container.remove(field_str)

    def get_person_positions(self):
        """ Matches and returns the person_position from the database. """

        try:
            physical_person = PhysicalPerson.objects.get(
                orcid=self.cleaned_data['orcid']
            )
        except ObjectDoesNotExist:
            # Non-existing PHysicalPerson so it doesn't have any PersonPositions associated
            return []

        person_positions = PersonPosition.objects.filter(
            person=physical_person,
            academic_title=self.cleaned_data['academic_title'],
            group=self.cleaned_data['group'],
            career_stage=self.cleaned_data['career_stage']
        )

        return person_positions

    def clean_phd_date(self):
        if 'phd_date' not in self.cleaned_data:
            return None

        if self.cleaned_data['phd_date'] == '':
            return None

        # It has the correct format mm-yyyy because the field has a validator
        # In the DB it's always yyyy-mm because the model has this validator (consistent with general mysql date format)
        month, year = self.cleaned_data['phd_date'].split('-')

        month_int = int(month)
        if month_int < 1 or month_int > 12:
            raise ValidationError(f'Invalid month: {month}', code='invalid', params={'value': month})

        return f'{year}-{month}'

    def clean(self):
        cd = super().clean()

        if self.errors:
            # If there are errors they might be related to orcid (e.g. using the example
            # ORCID iD, so cd['orcid'] doesn't exist. At this point we don't do further cleaning:
            # the user needs to fix the errors in the form before further cleaning is done.
            return cd

        # If ORCID iD is filled in: other fields are mandatory
        # if self._all_fields_are_optional and cd['orcid']:
        #     for field_str, field in self.fields.items():
        #         if field_str not in cd or not cd[field_str]:  # It needs to be in cd and have a value
        #             self.add_error(field_str, 'Mandatory field if ORCiD iD is filled in')
        #
        # if self._all_fields_are_optional and not cd['orcid']:
        #     for field_str, field in self.fields.items():
        #         if field_str in cd and cd[field_str]:
        #             self.add_error(field_str, 'It cannot contain any information if ORCiD ID is empty')

        return cd

    def save_person(self):
        cd = self.cleaned_data

        person_position = create_person_position(cd['orcid'], cd['first_name'], cd['surname'],
                                                 gender=cd.get('gender', None), phd_date=cd.get('phd_date', None),
                                                 academic_title=cd.get('academic_title'), group=cd.get('group'),
                                                 career_stage=cd.get('career_stage'),
                                                 organisation_names=cd.get('organisation_names', []))

        if cd.get('email', None):
            # Should this be in the model?
            # TODO: discuss how to replace emails
            email_contact = person_position.main_email_model()

            if email_contact is None:
                email_contact = Contact()
            email_contact.method = Contact.EMAIL
            email_contact.person_position = person_position

            email_contact.entry = cd.get('email')
            email_contact.save()

        if cd.get('phone', None):
            # Like before, should this be in the model and consolidated?
            # TODO: discuss how to replace phones and handling of multiple phones
            phone_contact = person_position.main_phone_model()

            if phone_contact is None:
                phone_contact = Contact()
            phone_contact.method = Contact.PHONE
            phone_contact.person_position = person_position

            phone_contact.entry = cd.get('phone').as_international
            phone_contact.save()

        return person_position
