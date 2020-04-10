from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.models import FinancialReport
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class FinancialReportItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])

        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)

        if self.instance and self.instance.signed_by is not None:
            self.fields['can_be_deleted'].initial = 0
            for widget_name in ['due_date', 'sent_date', 'reception_date']:
                self.fields[widget_name].disabled = True
                self.fields[widget_name].help_text = 'It cannot be changed since the financial report is signed'

        self.helper = FormHelper()
        self.helper.form_tag = False

        # It's included in the main formset, it avoids problems when adding new invoices and the jquery.formset.js
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                Div('can_be_deleted', hidden=True, css_class='can_be_deleted'),
                css_class='row', hidden=True
            ),
            Div(
                Div('due_date', css_class='col-3'),
                Div('reception_date', css_class='col-3'),
                Div('sent_date', css_class='col-3'),
                Div('signed_by', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('file', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        # TODO: Validate

    class Meta:
        model = FinancialReport
        fields = ['project', 'due_date', 'sent_date', 'reception_date', 'signed_by', 'file']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
        }
        labels = {'due_date': 'Due',
                  'reception_date': 'Received',
                  'sent_date': 'Sent for reviewing',
                  }


class FinancialReportsFormSet(BaseInlineFormSet):
    FORM_NAME = 'financial_reports_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = FinancialReportsFormSet.FORM_NAME

    def get_queryset(self):
        return super().get_queryset().order_by('reception_date')


FinancialReportsInlineFormSet = inlineformset_factory(Project, FinancialReport,
                                                      form=FinancialReportItemForm,
                                                      formset=FinancialReportsFormSet,
                                                      min_num=1, extra=0, can_delete=True)
