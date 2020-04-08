from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.models import Invoice
from project_core.models import Project
from project_core.utils.utils import format_date
from project_core.widgets import XDSoftYearMonthDayPickerInput


class InvoiceItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['paid_date'])

        if self.instance and self.instance.paid_date is not None:
            for widget_name in ['due_date', 'sent_date', 'reception_date']:
                self.fields[widget_name].disabled = True
                self.fields[widget_name].help_text = 'It cannot be changed since the invoice has a paid date'

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                css_class='row', hidden=True
            ),
            Div(
                Div('due_date', css_class='col-3'),
                Div('reception_date', css_class='col-3'),
                Div('sent_date', css_class='col-3'),
                Div('paid_date', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('amount', css_class='col-6'),
                Div('file', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data['project']
        project_starts = project.start_date
        project_ends = project.end_date

        errors = {}

        if cleaned_data['due_date'] is not None and cleaned_data['due_date'] < project_starts:
            errors['due_date'] = f'Due date cannot be before the project starting date ({format_date(project_starts)})'

        if cleaned_data['reception_date'] is not None and cleaned_data['reception_date'] > project_ends:
            errors['reception_date'] = f'Reception date cannot be after project end date ({format_date(project_ends)})'

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = Invoice
        fields = ['project', 'due_date', 'sent_date', 'reception_date', 'file', 'paid_date', 'amount']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
            'paid_date': XDSoftYearMonthDayPickerInput,
        }
        labels = {'due_date': 'Due',
                  'reception_date': 'Received',
                  'sent_date': 'Sent for payment',
                  'paid_date': 'Paid'
                  }


class InvoicesFormSet(BaseInlineFormSet):
    FORM_NAME = 'invoices_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = InvoicesFormSet.FORM_NAME

    def get_queryset(self):
        return super().get_queryset().order_by('-reception_date')


InvoicesInlineFormSet = inlineformset_factory(Project, Invoice, form=InvoiceItemForm, formset=InvoicesFormSet,
                                              min_num=1, extra=0, can_delete=True)
