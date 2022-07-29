from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from grant_management.models import CoInvestors
from project_core.models import Project


class PersonModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                css_class='row', hidden=True
            ),
            Div(
                Div('co_investigator', css_class='col-4'),
                Div('organisation', css_class='col-4'),
                Div('organisation_text', css_class='col-4'),
                css_class='row'
            ),
        )

    class Meta:
        model = CoInvestors
        fields = ['project', 'co_investigator', 'organisation', 'organisation_text']


class PersonsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('co_investigator')


PersonsInlineFormSet = inlineformset_factory(Project, CoInvestors, form=PersonModelForm,
                                               formset=PersonsFormSet,
                                               min_num=1, extra=0, can_delete=True)
