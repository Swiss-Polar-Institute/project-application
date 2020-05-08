from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms import BaseInlineFormSet, inlineformset_factory, ModelChoiceField

from grant_management.forms import utils
from grant_management.models import Installment, Invoice
from project_core.fields import AmountField
from project_core.models import Project
from project_core.templatetags.thousands_separator import thousands_separator
from project_core.widgets import XDSoftYearMonthDayPickerInput


class InstallmentTypeWithDescription(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name} - {obj.description}'


class InstallmentModelForm(forms.ModelForm):
    FORM_NAME = 'installment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])

        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)
        if self.instance and Invoice.objects.filter(installment=self.instance).exists():
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
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        project = cd['project']

        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        amount = cd.get('amount', None)

        DELETE = cd.get('DELETE', None)

        errors = {}

        if due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project_starts)

        if due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project_ends)

        amount_installments_to_now = InstallmentModelForm._total_amount_installments_for_project(project, self.instance)
        if (amount_installments_to_now + amount) > project.allocated_budget:
            errors[
                'amount'] = f'The amount of this installment will take this project over budget (Total installments until now: {thousands_separator(amount_installments_to_now)} CHF, Allocated budget: {thousands_separator(project.allocated_budget)} CHF).'

        if amount and self.instance:
            total_amount_invoices_for_installment = Invoice.objects.filter(installment=self.instance).aggregate(Sum('amount'))[
                'amount__sum']
            total_amount_invoices_for_installment = total_amount_invoices_for_installment or 0

            if total_amount_invoices_for_installment > amount:
                errors[
                    'amount'] = f'The new amount is not allowed because invoices have been paid for this installment in a higher amount ({thousands_separator(total_amount_invoices_for_installment)} CHF)'

        if DELETE and Invoice.objects.filter(installment=self.instance).exists():
            errors['DELETE'] = 'Cannot delete Installment: there are invoices assigned to this installment'

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _total_amount_installments_for_project(project, excluded_installment):
        excluded_installment_id = None

        if excluded_installment:
            excluded_installment_id = excluded_installment.id

        amount = Installment.objects. \
            filter(project=project). \
            exclude(id=excluded_installment_id). \
            aggregate(Sum('amount'))['amount__sum']

        return amount or 0

    class Meta:
        model = Installment
        fields = ['project', 'due_date', 'amount']
        field_classes = {'amount': AmountField}
        labels = {'due_date': 'Due'}
        help_texts = {'due_date': 'Date the installment is due'}
        widgets = {'due_date': XDSoftYearMonthDayPickerInput}


class InstallmentsFormSet(BaseInlineFormSet):
    FORM_NAME = 'installments_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = InstallmentsFormSet.FORM_NAME

    def get_queryset(self):
        return super().get_queryset().order_by('due_date')


InstallmentsInlineFormSet = inlineformset_factory(Project, Installment, form=InstallmentModelForm,
                                                  formset=InstallmentsFormSet,
                                                  min_num=1, extra=0, can_delete=True)
