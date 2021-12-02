from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from dal import autocomplete
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.urls import reverse

from .utils import get_field_information, cancel_edit_button, cancel_button
from ..models import PersonPosition, PhysicalPerson, Contact
from ..utils.orcid import orcid_div


class ContactForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        person__first_name = person__surname = person__orcid = main_email = None

        is_edit = self.instance and self.instance.pk and self.instance.person

        if is_edit:
            person__first_name = self.instance.person.first_name
            person__surname = self.instance.person.surname
            person__orcid = self.instance.person.orcid
            main_email = self.instance.main_email()
            cancel_html = cancel_edit_button(reverse('logged-person-position-detail', kwargs={'pk': self.instance.pk}))
        else:
            cancel_html = cancel_button(reverse('logged-person-position-list'))

        self.fields['person__orcid'] = forms.CharField(**get_field_information(PhysicalPerson, 'orcid'),
                                                       initial=person__orcid)
        self.fields['person__orcid'].required = False
        self.fields['person__orcid'].help_text += '. Please add the ORCID iD to avoid duplicates'

        self.fields['person__first_name'] = forms.CharField(**get_field_information(PhysicalPerson, 'first_name'),
                                                            initial=person__first_name)
        self.fields['person__surname'] = forms.CharField(**get_field_information(PhysicalPerson, 'surname'),
                                                         initial=person__surname)

        self.fields['email'] = forms.EmailField(initial=main_email, required=False)

        self.fields['privacy_policy'].help_text += '. Please make sure that the person has accepted the privacy policy' \
                                                   ' before adding them'

        self.fields['privacy_policy'].required = True

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            orcid_div('person__orcid'),
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
            ),
            Submit('submit', 'Save'),
            cancel_html
        )

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

        main_email = self.instance.main_email_model()
        if main_email:
            if self.cleaned_data['email']:
                main_email.entry = self.cleaned_data['email']
                main_email.save()
            else:
                main_email.delete()
        elif self.cleaned_data['email']:
            main_email, created = Contact.objects.get_or_create(person_position=model,
                                                                entry=self.cleaned_data['email'],
                                                                method=Contact.EMAIL)

        if commit:
            model.save()
            self.save_m2m()

        return model

    class Meta:
        model = PersonPosition
        fields = ['academic_title', 'group', 'privacy_policy', 'contact_newsletter', 'organisation_names']
        widgets = {'organisation_names': autocomplete.ModelSelect2Multiple(url='autocomplete-organisation-names')}
