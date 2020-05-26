from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import Publication
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class PublicationModelForm(forms.ModelForm):
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
                Div('reference', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('doi', css_class='col-6'),
                Div('published_date', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

    class Meta:
        model = Publication
        fields = ['project', 'doi', 'reference', 'title', 'published_date']
        widgets = {
            'published_date': XDSoftYearMonthDayPickerInput,
            'project': NumberInput,
        }
        labels = {'doi': 'DOI'}


class PublicationsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('published_date')


PublicationsInlineFormSet = inlineformset_factory(Project, Publication, form=PublicationModelForm,
                                                  formset=PublicationsFormSet,
                                                  min_num=1, extra=0, can_delete=True)
