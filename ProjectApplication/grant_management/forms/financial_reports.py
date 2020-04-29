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
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['approval_date'])

        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)

        if self.instance and self.instance.approved_by is not None:
            self.fields['can_be_deleted'].initial = 0
            for widget_name in ['due_date', 'sent_date', 'received_date']:
                self.fields[widget_name].disabled = True
                self.fields[widget_name].help_text = 'The financial report can no longer can be changed as it has ' \
                                                     'already been approved. Delete the date it was approved and try again.'

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
                Div('due_date', css_class='col-4'),
                Div('received_date', css_class='col-4'),
                Div('file', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('sent_date', css_class='col-4'),
                Div('approved_by', css_class='col-4'),
                Div('approval_date', css_class='col-4'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        project = cd['project']
        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        received_date = cd.get('received_date', None)
        sent_date = cd.get('sent_date', None)
        approval_date = cd.get('approval_date', None)
        approved_by = cd.get('approved_by', None)
        file = cd.get('file', None)

        errors = {}

        if due_date and due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project.start_date)

        if due_date and due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project.end_date)

        if received_date and received_date < project_starts:
            errors['received_date'] = utils.error_received_date_too_early(project.start_date)

        if sent_date and received_date and sent_date < received_date:
            errors['sent_date'] = 'Date sent for approval should be after the date the financial report was received'

        if approval_date and sent_date and approval_date < sent_date:
            errors['approval_date'] = 'Date the report was approved should be after the date it was sent for approval.'

        if not approved_by and approval_date:
            errors['approved_by'] = 'Please enter who approved the report (the approval date has been entered).'

        if not file and received_date:
            errors['file'] = 'Please attach the financial report file (the date received has been entered).'

        if not received_date and sent_date:
            errors['received_date'] = 'Please enter the date the financial report was received (the date it was ' \
                                       'sent for approval has been entered).'

        if not sent_date and approval_date:
            errors['sent_date'] = 'Please enter the date the financial report was sent for approval (the date it ' \
                                  'was approved has been entered).'

        if not approval_date and approved_by:
            errors['approval_date'] = 'Please enter the date the financial report was approved (the person who ' \
                                      'approved it has been entered).'

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = FinancialReport
        fields = ['project', 'due_date', 'received_date', 'sent_date', 'approval_date', 'approved_by', 'file']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'received_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'approval_date': XDSoftYearMonthDayPickerInput,
            'approved_by': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')
        }
        labels = {'due_date': 'Due',
                  'received_date': 'Received',
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
        return super().get_queryset().order_by('received_date')


FinancialReportsInlineFormSet = inlineformset_factory(Project, FinancialReport,
                                                      form=FinancialReportItemModelForm,
                                                      formset=FinancialReportsFormSet,
                                                      min_num=1, extra=0, can_delete=True)
