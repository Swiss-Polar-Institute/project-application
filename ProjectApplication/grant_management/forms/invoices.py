from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.db.models import Sum
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils.formats import number_format

from grant_management.forms.valid_if_empty import ValidIfEmptyModelForm
from grant_management.models import Invoice
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput
from . import utils


class InvoiceItemModelForm(ValidIfEmptyModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         fields_allowed_empty=['due_date'],
                         basic_fields=['project', 'id', 'DELETE', 'can_be_deleted'])

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['paid_date'])

        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)

        if self.instance and self.instance.paid_date is not None:
            self.fields['can_be_deleted'].initial = 0
            for widget_name in ['due_date', 'sent_date', 'reception_date', 'file', 'amount']:
                self.fields[widget_name].disabled = True
                self.fields[widget_name].help_text = 'Date cannot be changed as the invoice has already been paid'

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
                Div('paid_date', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('amount', css_class='col-6'),
                Div('file', css_class='col-6'),
                css_class='row'
            )
        )

    @staticmethod
    def _total_amount_invoices_for_project(project, excluded_invoice):
        excluded_invoice_id = None
        if excluded_invoice:
            excluded_invoice_id = excluded_invoice.id

        amount = Invoice.objects.filter(project=project).exclude(id=excluded_invoice_id).aggregate(Sum('amount'))[
            'amount__sum']
        return amount or 0

    def clean(self):
        cd = super().clean()

        project = cd['project']
        DELETE = cd.get('DELETE', None)

        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        reception_date = cd.get('reception_date', None)
        sent_date = cd.get('sent_date', None)
        paid_date = cd.get('paid_date', None)

        amount = cd.get('amount', None)
        file = cd.get('file', None)

        errors = {}

        if not due_date and (due_date or reception_date or sent_date or paid_date or amount or file):
            errors['due_date'] = f'Due date is required to create an invoice'

        if due_date and due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project_starts)

        if reception_date and reception_date < project_starts:
            errors['reception_date'] = utils.error_reception_date_too_early(project.start_date)

        if sent_date and reception_date and sent_date < reception_date:
            errors['sent_date'] = f'Date sent for payment should be after the date the invoice was received'

        if paid_date and sent_date and paid_date < sent_date:
            errors['paid_date'] = f'Date paid should be after the date the invoice was sent for payment'

        if due_date and due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project.end_date)

        if amount:
            amount_invoices_to_now = InvoiceItemModelForm._total_amount_invoices_for_project(project, self.instance)
            if (amount_invoices_to_now + amount) > project.allocated_budget:
                errors[
                    'amount'] = f'The amount of this invoice will take this project over budget (Total invoiced until now: {number_format(amount_invoices_to_now)} CHF, Allocated budget: {number_format(project.allocated_budget)} CHF).'

        if not file and reception_date:
            errors['file'] = f'Please attach the invoice file (a date received has been entered).'

        if not reception_date and sent_date:
            errors['reception_date'] = f'Please enter the date the invoice was received (a date sent for payment has been entered).'

        if not reception_date and paid_date:
            errors['reception_date'] = f'Please enter the date the invoice was recevived (a date paid has been entered).'

        if not amount and sent_date:
            errors['amount'] = f'Please enter the invoice amount (a date sent for payment has been entered).'

        if DELETE and paid_date:
            errors['paid_date'] = 'A paid invoice cannot be deleted. Delete the date paid and try again.'

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = Invoice
        fields = ['project', 'due_date', 'reception_date', 'sent_date', 'paid_date', 'amount', 'file']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
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
        return super().get_queryset().order_by('reception_date')


InvoicesInlineFormSet = inlineformset_factory(Project, Invoice, form=InvoiceItemModelForm, formset=InvoicesFormSet,
                                              min_num=1, extra=0, can_delete=True)
