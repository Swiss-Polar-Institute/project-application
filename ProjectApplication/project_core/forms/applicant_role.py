from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms

from project_core.models import Role


class ApplicantRole(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['role'] = forms.ModelChoiceField(queryset=Role.objects.all())
        self.fields['role_description'] = forms.CharField(widget=forms.Textarea())
        self.fields['competences'] = forms.CharField(widget=forms.Textarea())

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div(Div('role'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(Div('role_description'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(Div('competences'), css_class='col-12'),
                css_class='row'
            ),
        )

    def clean(self):
        return super().clean()
