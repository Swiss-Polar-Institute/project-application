from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import Dataset
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class DatasetModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['published_date'])

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
                Div('title', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('doi', css_class='col-6'),
                Div('url', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('published_date', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()
        return cd

    class Meta:
        model = Dataset
        fields = ['project', 'doi', 'url', 'title', 'published_date']
        widgets = {
            'published_date': XDSoftYearMonthDayPickerInput,
            'project': NumberInput,
        }
        labels = {'doi': 'DOI',
                  'url': 'URL'
                  }
        help_texts = {
            'doi': 'Digital object identifier of dataset, eg. 10.5281/zenodo.3260616'
        }


class DatasetsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('published_date')


DatasetInlineFormSet = inlineformset_factory(Project, Dataset, form=DatasetModelForm,
                                             formset=DatasetsFormSet,
                                             min_num=1, extra=0, can_delete=True)
