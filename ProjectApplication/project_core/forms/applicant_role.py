from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms

from project_core.models import RoleDescription


class RoleDescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('role', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('description', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('competences', css_class='col-12'),
                css_class='row'
            ),
        )

    def clean(self):
        return super().clean()

    class Meta:
        model = RoleDescription
        fields = ['role', 'description', 'competences']
