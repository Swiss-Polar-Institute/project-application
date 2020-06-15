import decimal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.safestring import mark_safe

from grant_management.forms import utils
from grant_management.forms.invoices import html_message
from grant_management.models import Installment, Invoice
from project_core.fields import AmountField
from project_core.models import Project
from project_core.templatetags.thousands_separator import thousands_separator
from project_core.widgets import XDSoftYearMonthDayPickerInput


class InstallmentModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])

        message = ''
        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)
        if self.instance and self.instance.id and Invoice.objects.filter(installment=self.instance).exists():
            message = 'This installment cannot be deleted because invoices are attached to it'
            self.fields['can_be_deleted'].initial = 0

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

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
                Div('amount', css_class='col-4'),
                Div(HTML(html_message(message)), css_class='col-4 to-delete'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        if self.errors:
            return cd

        project = cd['project']

        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        amount = cd.get('amount', None)

        DELETE = cd.get('DELETE', None)

        errors = {}

        total_invoiced = None

        if self.instance:
            total_invoiced = self.instance.invoice_set.all().aggregate(Sum('amount'))['amount__sum']

        if amount and total_invoiced and amount < total_invoiced:
            errors[
                'amount'] = f'New installment amount {thousands_separator(amount)} CHF is lower than currently invoiced to this installment ({thousands_separator(total_invoiced)} CHF)'

        if amount > project.allocated_budget:
            errors['amount'] = 'This amount is greater than the total project allocated budget'

        if due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project)

        if due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project)

        if DELETE and Invoice.objects.filter(installment=self.instance).exists():
            errors['DELETE'] = 'Cannot delete Installment: there are invoices assigned to this installment'

        if project.is_active() is False:
            raise ValidationError(f'Cannot modify installments for this project: the status is {project.status}')

        if errors:
            raise ValidationError(errors)

        return cd

    class Meta:
        model = Installment
        fields = ['project', 'due_date', 'amount']
        field_classes = {'amount': AmountField}
        labels = {'due_date': 'Due',
                  'amount': 'Amount (CHF)'
                  }
        help_texts = {'due_date': 'Date the installment is due'}
        widgets = {'due_date': XDSoftYearMonthDayPickerInput}


class InstallmentsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean(self):
        super().clean()

        if not self.is_valid():
            # if one of the budget items is not valid: doesn't validate the general form
            # E.g. if an amount is negative it will have an error in the amount but the
            # amount is removed from the form.cleaned_data
            return

        budget_amount = decimal.Decimal('0.00')
        maximum_budget = self.instance.allocated_budget

        for installment_form in self.forms:
            amount = installment_form.cleaned_data['amount'] or 0

            budget_amount += amount

        if budget_amount > maximum_budget:
            raise forms.ValidationError(
                f'Total allocated budget for this project is {thousands_separator(maximum_budget)} CHF.'
                f' The current total of the installments is {thousands_separator(budget_amount)} CHF which exceeds the allocated budget.'
            )

    def get_queryset(self):
        return super().get_queryset().order_by('due_date')

    def extra_information(self):
        return mark_safe(f'<p><b>Budget allocated</b>: {thousands_separator(self.instance.allocated_budget)} CHF</p>')


InstallmentsInlineFormSet = inlineformset_factory(Project, Installment, form=InstallmentModelForm,
                                                  formset=InstallmentsFormSet,
                                                  min_num=1, extra=0, can_delete=True)
