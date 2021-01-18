from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from dal import autocomplete
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from project_core.forms.person import PersonForm
from project_core.forms.utils import keywords_validation
from project_core.models import Proposal, ProposalScientificCluster


class ScientificClusterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._person_form = self._get_person_form()

        self.helper = FormHelper()
        self.helper.form_tag = False

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
            Div(
                Div('keywords', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(
                HTML('<h3>Sub-PI</h3>'), css_class='col-12'),
                css_class='row'
                ),
            *self._person_form.helper.layout
        )
        self.fields.update(self._person_form.fields)

    def _get_person_form(self):
        help_texts = {'orcid': "Sub-PI\'s ORCID iD (e.g.: 0000-0002-1825-0097)",
                      'first_name': 'Name populated from the ORCID record. If you would like to change it, amend it in ORCID',
                      'surname': 'Surname populated from the ORCID record. If you would like to change it, amend it in ORCID',
                      'phd_date': 'If applicable, enter the date that the sub-PI was awarded their PhD (mm-yyyy)',
                      'email': 'Enter a valid email address for the sub-PI. Note this email address will not receive a confirmation email upon submission',
                      'organisation_names': 'Select the organisation(s) to which the sub-PI is affiliated for the purposes of this proposal. If they are not available amongst the options provided, type the full name and click on “Create”',
                      'group': 'Type the names of the group(s) or laboratories to which the sub-PI is affiliated for the purposes of this proposal'}

        # This is a QueryDict, not a dict
        person_form_data = self.data.copy()
        person_form_data.clear()

        # to get the fields
        temporary_person_form = PersonForm(help_texts=help_texts)

        for field_name in self.data.keys():
            if field_name in ['encoding', 'csrfmiddlewaretoken']:
                person_form_data.setlist(field_name, self.data.getlist(field_name))

            if not field_name.startswith(self.prefix):
                continue

            person_form_field_name = field_name[len(f'{self.prefix}-'):]

            if person_form_field_name in temporary_person_form.fields:
                person_form_data.setlist(person_form_field_name, self.data.getlist(field_name))

        sub_pi = self.instance.sub_pi if self.instance and hasattr(self.instance, 'sub_pi') else None

        person = PersonForm(data=person_form_data, person_position=sub_pi, help_texts=help_texts)
        return person

    def is_valid(self):
        scientific_cluster_is_valid = super().is_valid()

        return scientific_cluster_is_valid and self._person_form.is_valid()

    def clean(self):
        cd = super().clean()
        errors = {}

        if 'keywords' not in self.errors:
            # Probably there are no keywords... here we validate the minimum number of keywords
            keywords_validation(errors, self.cleaned_data, 'keywords')

        if errors:
            raise forms.ValidationError(errors)

        return cd

    def save(self, *args, **kwargs):
        sub_pi = self._person_form.save_person()

        instance = super().save(commit=False)
        instance.sub_pi = sub_pi

        instance.save()

        self.save_m2m()  # For the keywords

        return instance

    class Meta:
        model = ProposalScientificCluster
        fields = ['proposal', 'title', 'keywords']
        widgets = {'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords')}
        help_texts = {'title': 'Title of the research cluster',
                      'keywords': 'Select at least 5 keywords that describe the research cluster. If the keywords you are looking for do not exist, then add each term separately'}


class ScientificClustersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('id')

    def save(self, *args, **kwargs):
        self.is_valid()
        return super().save(*args, **kwargs)


ScientificClustersInlineFormSet = inlineformset_factory(Proposal, ProposalScientificCluster, form=ScientificClusterForm,
                                                        formset=ScientificClustersFormSet,
                                                        min_num=1, extra=0, can_delete=True)
