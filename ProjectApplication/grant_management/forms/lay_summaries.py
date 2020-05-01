from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import LaySummary
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class LaySummaryModelForm(forms.ModelForm):
    FORM_NAME = 'lay_summary'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])

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
                Div('due_date', css_class='col-4'),
                Div('received_date', css_class='col-4'),
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
        received_date = cd.get('received_date', None)
        sent_date = cd.get('sent_date', None)
        text = cd.get('text', '')
        author = cd.get('author', None)
        lay_summary_type = cd.get('lay_summary_type', None)

        errors = {}

        if author is None and text != '':
            errors['author'] = 'Please select the author if there is text'
        if author is None and received_date is not None:
            errors['author'] = 'Please select the author if a received date has been entered'
        if author is not None and text is None:
            errors['text'] = 'Please enter the text if there is an author'
        if text != '' and received_date is None:
            errors['received_date'] = 'Please enter the date the lay summary was received if there is text'
        if text != '' and lay_summary_type is None:
            errors['lay_summary_type'] = 'Please enter the type of lay summary if there is text'
        if received_date is not None and text is None:
            errors['text'] = 'Please enter the text if the received date has been entered'


        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = LaySummary
        fields = ['project', 'lay_summary_type', 'due_date', 'received_date', 'text', 'author']
        labels = {'text': 'Lay summary', 'due_date': 'Due', 'received_date': 'Received'}
        help_texts = {'due_date': 'Date the lay summary is due', 'received_date': 'Date the lay summary was received',
                      'text': None}
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_for_approval_date': XDSoftYearMonthDayPickerInput,
            'received_date': XDSoftYearMonthDayPickerInput,
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
        return super().get_queryset().order_by('due_date')


LaySummariesInlineFormSet = inlineformset_factory(Project, LaySummary, form=LaySummaryModelForm,
                                                  formset=LaySummariesFormSet,
                                                  min_num=1, extra=0, can_delete=True)
