from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from dal import autocomplete
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import Milestone
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class MilestoneModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                css_class='row', hidden=True
            ),
            Div(
                Div('due_date', css_class='col-2'),
                Div('category', css_class='col-4'),
                Div('text', css_class='col-6'),
                css_class='row'
            ),
        )

    def clean(self):
        cd = super().clean()

    class Meta:
        model = Milestone
        fields = ['project', 'due_date', 'category', 'text']
        widgets = {
            'project': NumberInput,
            'due_date': XDSoftYearMonthDayPickerInput,
            'category': autocomplete.ModelSelect2(url='logged-grant_management-autocomplete-milestones-names')
        }


class MilestoneFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('due_date')


MilestoneInlineFormSet = inlineformset_factory(Project, Milestone, form=MilestoneModelForm,
                                               formset=MilestoneFormSet,
                                               min_num=1, extra=0, can_delete=True)
