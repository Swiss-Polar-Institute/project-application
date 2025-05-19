from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from dal import autocomplete
from django import forms
from django.urls import reverse
from django.forms import BaseInlineFormSet, inlineformset_factory

from grant_management.models import CarbonEmission
from project_core.forms.utils import cancel_edit_button
from project_core.models import Project


class CarbonEmissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div('file', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('estimate_carbon_emission', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div('effective_carbon_emission_file', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('effective_carbon_emission', css_class='col-6'),
                css_class='row'
            )
        )


    class Meta:
        model = CarbonEmission
        fields = ['project', 'estimate_carbon_emission', 'effective_carbon_emission_file', 'effective_carbon_emission', 'file']
        labels = {'file': 'Estimate Carbon Emission File', 'effective_carbon_emission_file': 'Effective Carbon Emission File'}


class CarbonEmissionFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('project')

CarbonEmissionInlineFormSet = inlineformset_factory(Project, CarbonEmission, form=CarbonEmissionForm,
                                               formset=CarbonEmissionFormSet,
                                               min_num=1, extra=0, can_delete=True)

