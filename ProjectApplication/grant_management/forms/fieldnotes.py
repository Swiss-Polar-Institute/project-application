from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import FieldNote
from project_core.models import Project


class FieldNoteModelForm(forms.ModelForm):
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
                Div('title', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('url', css_class='col-12'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()
        return cd

    class Meta:
        model = FieldNote
        fields = ['project', 'url', 'title']
        widgets = {
            'project': NumberInput,
        }
        labels = {
            'url': 'URL'
        }


class FieldNoteFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


FieldNoteInlineFormSet = inlineformset_factory(Project, FieldNote, form=FieldNoteModelForm,
                                               formset=FieldNoteFormSet,
                                               min_num=1, extra=1, can_delete=True)
