from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput
from django.urls import reverse

from grant_management.models import LaySummary
from project_core.forms.utils import cancel_edit_button
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class LaySummaryModelForm(forms.ModelForm):
    FORM_NAME = 'lay_summary'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                css_class='row', hidden=True
            ),
            Div(
                Div('due_date', css_class='col-4'),
                Div('sent_date', css_class='col-4'),
                Div('reception_date', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('text', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('author', css_class='col-6'),
                Div('lay_summary_type', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        due_date = cd.get('due_date', None)
        reception_date = cd.get('reception_date', None)
        sent_date = cd.get('sent_date', None)
        text = cd.get('text', None)
        author = cd.get('author', None)
        lay_summary_type = cd.get('lay_summary_type', None)

        errors = {}

        if author is None and text is not None:
            errors['author'] = 'Please select the author if there is text'

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = LaySummary
        fields = ['project', 'lay_summary_type', 'due_date', 'sent_date', 'reception_date', 'text', 'author']
        labels = {'text': 'Lay summary'}
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
            'project': NumberInput
        }


class LaySummariesFormSet(BaseInlineFormSet):
    FORM_NAME = 'lay_summaries_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = LaySummariesFormSet.FORM_NAME

    def get_queryset(self):
        return super().get_queryset().order_by('reception_date')


LaySummariesInlineFormSet = inlineformset_factory(Project, LaySummary, form=LaySummaryModelForm,
                                                  formset=LaySummariesFormSet,
                                                  min_num=1, extra=0, can_delete=True)
