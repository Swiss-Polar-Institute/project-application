from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, HTML
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet, ModelChoiceField
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from ProjectApplication import settings
from comments.forms.comment import CommentForm
from grant_management.models import Invoice, LaySummary, LaySummaryType, Installment
from project_core.models import Project
from project_core.templatetags.ordinal import ordinal
from project_core.templatetags.thousands_separator import thousands_separator
from project_core.utils.utils import format_date
from project_core.widgets import XDSoftYearMonthDayPickerInput
from . import utils


class InstallmentModelChoiceField(ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sequence = 0

    def label_from_instance(self, obj):
        self._sequence += 1
        amount = thousands_separator(obj.amount)
        return mark_safe(f'{ordinal(self._sequence)} - {format_date(obj.due_date)} - {amount} CHF')


class InvoiceItemModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)  # When the form is created to visualise user is not needed
        # user is used when saving comments at the moment

        project = kwargs.pop('project')

        super().__init__(*args, **kwargs)

        self._comment_form = None

        if self.instance and self.instance.id:
            self.comment_prefix = f'comment-invoice-{self.instance.id}'
            self.comments = self.instance.comments()
            self.comment_count = len(self.comments)
            self.comments_save_text = 'Save Finances'

            self._comment_form = CommentForm(form_action=reverse('logged-proposal-evaluation-comment-add',
                                                                 kwargs={'pk': self.instance.id}),
                                             category_queryset=self.instance.comment_object().category_queryset(),
                                             prefix=CommentForm.FORM_NAME,
                                             form_tag=False,
                                             fields_required=False)
            self.fields.update(self._comment_form.fields)

        self.fields['installment'].queryset = Installment.objects.filter(project=project).order_by('due_date')

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_for_payment_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['paid_date'])

        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)

        if self.instance and self.instance.paid_date is not None:
            self.fields['can_be_deleted'].initial = 0
            for field_name in ['due_date', 'received_date', 'sent_for_payment_date', 'file', 'amount', 'installment']:
                self.fields[field_name].disabled = True
                self.fields[field_name].help_text = f'Invoice cannot be changed as it has already been paid. ' \
                                                    f'Delete the date it was paid and try again'

        self.helper = FormHelper()
        self.helper.form_tag = False

        # It's included in the main formset, it avoids problems when adding new invoices and the jquery.formset.js
        self.helper.disable_csrf = True

        divs = [
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                Div('can_be_deleted', hidden=True, css_class='can_be_deleted'),
                css_class='row', hidden=True
            ),
            Div(
                Div('installment', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('due_date', css_class='col-4'),
                Div('received_date', css_class='col-4'),
                Div('file', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('amount', css_class='col-4'),
                Div('sent_for_payment_date', css_class='col-4'),
                Div('paid_date', css_class='col-4'),
                css_class='row'
            )
        ]

        if self._comment_form:
            divs += Div(HTML("{% include 'comments/_accordion-comment-list-fields-for-new.tmpl' %}"))

        self.helper.layout = Layout(*divs)

    def clean(self):
        cd = super().clean()

        project = cd['project']
        DELETE = cd.get('DELETE', None)

        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        received_date = cd.get('received_date', None)
        sent_for_payment_date = cd.get('sent_for_payment_date', None)
        paid_date = cd.get('paid_date', None)
        installment = cd.get('installment', None)

        amount = cd.get('amount', None)
        file = cd.get('file', None)

        errors = {}
        sent_for_payment_errors = []

        today = timezone.now().date()

        if received_date and received_date > today:
            errors['received_date'] = 'Received date cannot be in the future'

        if sent_for_payment_date and sent_for_payment_date > today:
            errors['sent_for_payment_date'] = 'Sent for payment date cannot be in the future'

        if paid_date and paid_date > today:
            errors['paid_date'] = 'Paid date cannot be in the future'

        if not due_date and (due_date or received_date or sent_for_payment_date or paid_date or amount or file):
            errors['due_date'] = f'Due date is required to create an invoice'

        if due_date and due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project_starts)

        if received_date and received_date < project_starts:
            errors['received_date'] = utils.error_received_date_too_early(project.start_date)

        if sent_for_payment_date and received_date and sent_for_payment_date < received_date:
            sent_for_payment_errors.append(
                f'Date sent for payment should be after the date the invoice was received date')

        if paid_date and sent_for_payment_date and paid_date < sent_for_payment_date:
            errors['paid_date'] = f'Date paid should be after the date the invoice was sent for payment'

        if due_date and due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project.end_date)

        if not file and received_date:
            errors['file'] = f'Please attach the invoice file (a date received has been entered).'

        if not received_date and sent_for_payment_date:
            errors[
                'received_date'] = f'Please enter the date the invoice was received (a date sent for payment has been entered).'

        if not received_date and paid_date:
            errors[
                'received_date'] = f'Please enter the date the invoice was recevived (a date paid has been entered).'

        if not amount and sent_for_payment_date:
            errors['amount'] = f'Please enter the invoice amount (a date sent for payment has been entered).'

        if sent_for_payment_date is not None and (
                hasattr(project, 'grantagreement') is False or project.grantagreement.file is None):
            grant_agreement_url = reverse('logged-grant_management-grant_agreement-add', kwargs={'project': project.id})
            sent_for_payment_errors.append(
                f'Please attach the <a href="{grant_agreement_url}">grant agreement<a> in order to enter the date the invoice was sent for payment')

        original_lay_summary_type = LaySummaryType.objects.get(name=settings.LAY_SUMMARY_ORIGINAL)
        if sent_for_payment_date and LaySummary.objects.filter(project=project).filter(
                lay_summary_type=original_lay_summary_type).exists() is False:
            lay_summary_url = reverse('logged-grant_management-lay_summaries-update', kwargs={'project': project.id})
            sent_for_payment_errors.append(
                f'Please attach the <a href="{lay_summary_url}">original lay summary</a> in order to send the invoice for payment')

        if amount and installment and amount > installment.amount:
            errors['amount'] = 'Invoice amount is greater than the installment amount'

        if sent_for_payment_date is None and paid_date:
            sent_for_payment_errors.append('Please fill in sent for payment if the invoice is paid')

        if sent_for_payment_errors:
            errors['sent_for_payment_date'] = mark_safe('<br>'.join(sent_for_payment_errors))

        if DELETE and paid_date:
            errors['paid_date'] = 'A paid invoice cannot be deleted. Delete the date paid and try again.'

        if errors:
            raise forms.ValidationError(errors)

    def save(self, *args, **kwargs):
        assert self._user

        comment_category = self.cleaned_data.get('category', None)
        comment_text = self.cleaned_data.get('text', None)

        if comment_text:
            data = {'category': comment_category,
                    'text': comment_text}

            comment_form = CommentForm(data=data,
                                       form_action=reverse('logged-proposal-evaluation-comment-add',
                                                           kwargs={'pk': self.instance.id}),
                                       category_queryset=self.instance.comment_object().category_queryset(),
                                       form_tag=False)
            comment_form.is_valid()
            # TODO: as it is now: it's always valid (combobox mandatory selection for internal users). In the is_valid()
            # of the Invoice it should reject it if it's not valid
            comment_form.save(parent=self.instance,
                              user=self._user)

        super().save(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = ['project', 'installment', 'due_date', 'received_date', 'sent_for_payment_date', 'paid_date', 'amount',
                  'file']
        field_classes = {'installment': InstallmentModelChoiceField}
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'received_date': XDSoftYearMonthDayPickerInput,
            'sent_for_payment_date': XDSoftYearMonthDayPickerInput,
            'paid_date': XDSoftYearMonthDayPickerInput,
        }
        labels = {'due_date': 'Due',
                  'received_date': 'Received',
                  'sent_for_payment_date': 'Sent for payment',
                  'paid_date': 'Paid'
                  }
        help_texts = {'due_date': 'Date the invoice is due', 'received_date': 'Date the invoice was received'}


class InvoicesFormSet(BaseInlineFormSet):
    wants_user = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('received_date')

    def clean(self):
        super().clean()

        if not self.is_valid():
            # if one of the budget items is not valid: doesn't validate the general form
            # E.g. if an amount is negative it will have an error in the amount but the
            # amount is removed from the form.cleaned_data
            return

        installment_to_amounts = {}

        for invoice_form in self.forms:
            if not invoice_form.cleaned_data['installment']:
                continue

            amount = invoice_form.cleaned_data['amount'] or 0   # It's None if the amount is not filled in

            if invoice_form.cleaned_data['installment'].id in installment_to_amounts:
                installment_to_amounts[invoice_form.cleaned_data['installment'].id] += amount
            else:
                installment_to_amounts[invoice_form.cleaned_data['installment'].id] = amount

        errors = []
        for installment_id, invoiced_amount in installment_to_amounts.items():
            installment = Installment.objects.get(id=installment_id)
            installment_amount_allocated = installment.amount

            if invoiced_amount > installment_amount_allocated:
                errors.append(
                    f'Over budget for installment due {installment.due_date}, total allocated {thousands_separator(installment.amount)} CHF. Total invoiced: {thousands_separator(invoiced_amount)} CHF')

        if errors:
            raise forms.ValidationError(errors)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['project'] = self.instance
        return kwargs


InvoicesInlineFormSet = inlineformset_factory(Project, Invoice, form=InvoiceItemModelForm, formset=InvoicesFormSet,
                                              min_num=1, extra=0, can_delete=True)
