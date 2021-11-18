from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from grant_management.models import Location
from project_core.models import Project


class LocationModelForm(forms.ModelForm):
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
                Div('name', css_class='col-6'),
                Div('latitude', css_class='col-3'),
                Div('longitude', css_class='col-3'),
                css_class='row'
            ),
        )

    class Meta:
        model = Location
        fields = ['project', 'name', 'latitude', 'longitude']


class LocationsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('name')


LocationsInlineFormSet = inlineformset_factory(Project, Location, form=LocationModelForm,
                                               formset=LocationsFormSet,
                                               min_num=1, extra=0, can_delete=True)
