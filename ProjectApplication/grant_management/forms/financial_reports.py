from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from dal import autocomplete
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.forms.valid_if_empty import ValidIfEmptyModelForm
from grant_management.models import FinancialReport
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput
from . import utils


class FinancialReportItemModelForm(ValidIfEmptyModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         fields_allowed_empty=['due_date'],
                         basic_fields=['project', 'id', 'DELETE', 'can_be_deleted'])

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['approval_date'])

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
                Div('approval_date', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('signed_by', css_class='col-6'),
                Div('file', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        project = cd['project']
        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        reception_date = cd.get('reception_date', None)
        sent_date = cd.get('sent_date', None)
        approval_date = cd.get('approval_date', None)
        signed_by = cd.get('signed_date', None)
        file = cd.get('file', None)

        errors = {}

        if due_date and due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project.start_date)

        if due_date and due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project.end_date)

        if reception_date and reception_date < project_starts:
            errors['reception_date'] = utils.error_reception_date_too_early(project.start_date)

        if sent_date and reception_date and sent_date < reception_date:
            errors['sent_date'] = 'Sent date cannot be before date received'

        if approval_date and sent_date and approval_date < sent_date:
            errors['approval_date'] = 'Approval date needs to be after send for review date'

        if not signed_by and approval_date:
            errors['signed_by'] = 'Signed by required if the report has an approval date'

        if not file and reception_date:
            errors['file'] = 'File is required if reception date is filled in'

        if not reception_date and sent_date:
            errors['reception_date'] = 'Reception date is required if send date is filled in'

        if not sent_date and approval_date:
            errors['sent_date'] = 'Send date is required if approval date is filled in'

        if not approval_date and signed_by:
            errors['approval_date'] = 'Approval date is required if the financial report is signed'

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = FinancialReport
        fields = ['project', 'due_date', 'reception_date', 'sent_date', 'approval_date', 'signed_by', 'file']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'approval_date': XDSoftYearMonthDayPickerInput,
            'signed_by': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')
        }
        labels = {'due_date': 'Due',
                  'reception_date': 'Received',
                  'sent_date': 'Sent for review',
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
                                                      form=FinancialReportItemModelForm,
                                                      formset=FinancialReportsFormSet,
                                                      min_num=1, extra=0, can_delete=True)
