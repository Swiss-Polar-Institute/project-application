from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms

from project_core.forms.utils import LabelAndOrderNameChoiceField
from project_core.models import RoleDescription
from variable_templates.utils import apply_templates_to_fields


class RoleDescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        call = kwargs.pop('call', None)
        super().__init__(*args, **kwargs)

        apply_templates_to_fields(self.fields, call)

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
        help_texts = {'role': 'Select the role of the applicant in the proposed {{ activity }}',
                      'description': "Description of the applicant's role",
                      'competences': "Description of the applicant's key competences"
                      }
        field_classes = {'role': LabelAndOrderNameChoiceField}
