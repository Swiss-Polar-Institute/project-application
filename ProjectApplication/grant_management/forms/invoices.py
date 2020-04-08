from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.models import Invoice
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class InvoiceItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['sent_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['reception_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['paid_date'])

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                css_class='row'
            ),
            Div(
                Div('reception_date', css_class='col-3'),
                Div('due_date', css_class='col-3'),
                Div('sent_date', css_class='col-3'),
                Div('paid_date', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('amount', css_class='col-6'),
                Div('file', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div(Field('DELETE', css_class='col-12'),
                    css_class='row')
            )
        )

    class Meta:
        model = Invoice
        fields = ['project', 'due_date', 'sent_date', 'reception_date', 'file', 'paid_date', 'amount']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'sent_date': XDSoftYearMonthDayPickerInput,
            'reception_date': XDSoftYearMonthDayPickerInput,
            'paid_date': XDSoftYearMonthDayPickerInput,
        }


class InvoicesFormSet(BaseInlineFormSet):
    FORM_NAME = 'invoices_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = InvoicesFormSet.FORM_NAME


InvoicesInlineFormSet = inlineformset_factory(Project, Invoice, form=InvoiceItemForm, formset=InvoicesFormSet, extra=0,
                                              can_delete=True)
