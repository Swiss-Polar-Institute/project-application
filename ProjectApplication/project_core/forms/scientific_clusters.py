from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.http import QueryDict

from project_core.forms.person import PersonForm
from project_core.models import Proposal, ProposalScientificCluster


class ScientificClusterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._person_form = PersonForm()

        self.helper = FormHelper()
        self.helper.form_tag = False

        # self.helper.disable_csrf = True  # checked in the higher form level

        self.helper.layout = Layout(
            Div(
                Div('proposal', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                css_class='row', hidden=True
            ),
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),

            *self._person_form.helper.layout
        )
        self.fields.update(self._person_form.fields)

    def is_valid(self):
        scientific_cluster_is_valid = super().is_valid()

        # This is a QueryDict, not a dict
        person_form_data = self.data.copy()
        person_form_data.clear()

        for field_name in self.data.keys():
            if field_name in ['encoding', 'csrfmiddlewaretoken']:
                person_form_data.setlist(field_name, self.data.getlist(field_name))

            if not field_name.startswith(self.prefix):
                continue

            person_form_field_name = field_name[len(f'{self.prefix}-'):]

            if person_form_field_name in self._person_form.fields:
                person_form_data.setlist(person_form_field_name, self.data.getlist(field_name))

        person = PersonForm(data=person_form_data)

        person_is_valid = person.is_valid()

        return scientific_cluster_is_valid and person_is_valid

    def clean(self):
        cd = super().clean()

        return cd

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)

        return super().save(*args, **kwargs)

    class Meta:
        model = ProposalScientificCluster
        fields = ['proposal', 'title']


class ScientificClustersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('id')


ScientificClustersInlineFormSet = inlineformset_factory(Proposal, ProposalScientificCluster, form=ScientificClusterForm,
                                                        formset=ScientificClustersFormSet,
                                                        min_num=1, extra=0, can_delete=True)
