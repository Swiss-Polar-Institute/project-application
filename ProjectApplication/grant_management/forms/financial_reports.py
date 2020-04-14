from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from dal import autocomplete
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
                Div('approval_date', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('signed_by', css_class='col-6'),
                Div('file', css_class='col-6'),
                css_class='row'
            )
        )

    def _is_empty(self):
        # Returns True if no data has been entered (based on self.cleaned_data)
        # This is used in order to show a Financial Report but let the user to not enter anything
        # (so it plays easily with the jQuery modelset)
        # TODO: avoid this

        for field_name in ['due_date', 'sent_date', 'reception_date', 'signed_by', 'approval_date', 'file']:
            if field_name in self.cleaned_data and self.cleaned_data[field_name] is not None:
                return False

        return True

    def is_valid(self):
        valid = super().is_valid()

        return valid or self._is_empty()

    def save(self, *args, **kwargs):
        if self._is_empty():
            return None

        super().save(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        errors = {}

        if cleaned_data['file'] is None and cleaned_data['signed_by']:
            errors['file'] = 'Report needs to be attached if it is signed'

        if cleaned_data['reception_date'] is not None and cleaned_data['sent_date'] is not None and \
                cleaned_data['reception_date'] > cleaned_data['sent_date']:
            errors['reception_date'] = 'Received date needs to be before sent date'

        # if cleaned_data['due_date'] is None and cleaned_data['sent_date'] is None and cleaned_data[
        #     'reception_date'] is None and cleaned_data['signed_by'] is None and cleaned_data['file'] is None:
        #     raise forms.ValidationError('Please enter more data to create the financial report')
        #
        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = FinancialReport
        fields = ['project', 'due_date', 'sent_date', 'reception_date', 'signed_by', 'approval_date', 'file']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
            'approval_date': XDSoftYearMonthDayPickerInput,
            'signed_by': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')
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
