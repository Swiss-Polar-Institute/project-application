from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

from ..models import PersonPosition, PhysicalPerson
from django.forms import ModelForm
from django import forms
from .utils import get_field_information

class ContactForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        person__first_name = person__surname = main_email = None

        if self.instance and self.instance.person:
            person__first_name = self.instance.person.first_name
            person__surname = self.instance.person.surname
            main_email = self.instance.main_email()

        self.fields['person__first_name'] = forms.CharField(**get_field_information(PhysicalPerson, 'first_name'),
                                                            initial=person__first_name)
        self.fields['person__surname'] = forms.CharField(**get_field_information(PhysicalPerson, 'surname'),
                                                         initial=person__surname)

        self.fields['data_policy'].disabled = True
        self.fields['contact_newsletter'].disabled = True

        self.fields['email'] = forms.EmailField(initial=main_email)

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(
                Div('academic_title', css_class='col-2'),
                Div('person__first_name', css_class='col-5'),
                Div('person__surname', css_class='col-5'),
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
                Div('data_policy', css_class='col-6'),
                Div('contact_newsletter', css_class='col-6'),
                css_class='row'
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = PersonPosition
        fields = ['academic_title', 'group', 'data_policy', 'contact_newsletter']
