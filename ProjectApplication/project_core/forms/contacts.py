from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from dal import autocomplete
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm

from .utils import get_field_information
from ..models import PersonPosition, PhysicalPerson, Contact


class ContactForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        person__first_name = person__surname = main_email = None

        if self.instance and self.instance.pk and self.instance.person:
            person__first_name = self.instance.person.first_name
            person__surname = self.instance.person.surname
            main_email = self.instance.main_email()

        self.fields['person__first_name'] = forms.CharField(**get_field_information(PhysicalPerson, 'first_name'),
                                                            initial=person__first_name)
        self.fields['person__surname'] = forms.CharField(**get_field_information(PhysicalPerson, 'surname'),
                                                         initial=person__surname)

        self.fields['privacy_policy'].disabled = True
        self.fields['contact_newsletter'].disabled = True

        self.fields['email'] = forms.EmailField(initial=main_email, required=False)

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(
                Div('academic_title', css_class='col-2'),
                Div('person__first_name', css_class='col-5'),
                Div('person__surname', css_class='col-5'),
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
                Div('email', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('privacy_policy', css_class='col-6'),
                Div('contact_newsletter', css_class='col-6'),
                css_class='row'
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):
        super().clean()

        if self.instance is None or self.instance.pk is None:
            # Creating a new one. Let's avoid creating duplicates and inform the user
            try:
                physical_person = PhysicalPerson.objects.get(first_name=self.cleaned_data['person__first_name'],
                                                             surname=self.cleaned_data['person__surname'])
                raise forms.ValidationError('Cannot create this contact: person already exists')

            except ObjectDoesNotExist:
                pass

    def save(self, commit=True):
        model = super().save(False)

        if model.person_id:
            model.person.first_name = self.cleaned_data['person__first_name']
            model.person.surname = self.cleaned_data['person__surname']

        else:
            model.person, created = PhysicalPerson.objects.get_or_create(
                first_name=self.cleaned_data['person__first_name'],
                surname=self.cleaned_data['person__surname'])

        if commit:
            model.person.save()
            model.save()

        if self.cleaned_data['email']:
            main_email = self.instance.main_email_model()
            if main_email:
                main_email.entry = self.cleaned_data['email']
            else:
                main_email, created = Contact.objects.get_or_create(person_position=model,
                                                                    entry=self.cleaned_data['email'],
                                                                    method=Contact.EMAIL)

            if commit:
                main_email.save()

        if commit:
            model.save()
            self.save_m2m()

        return model

    class Meta:
        model = PersonPosition
        fields = ['academic_title', 'group', 'privacy_policy', 'contact_newsletter', 'organisation_names']
        widgets = {'organisation_names': autocomplete.ModelSelect2Multiple(url='autocomplete-organisation-names')}
