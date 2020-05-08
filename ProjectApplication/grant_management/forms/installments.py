from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, ModelChoiceField

from grant_management.models import Installment
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class InstallmentTypeWithDescription(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name} - {obj.description}'


class InstallmentModelForm(forms.ModelForm):
    FORM_NAME = 'installment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
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

    class Meta:
        model = Installment
        fields = ['project', 'due_date', 'amount']
        labels = {'due_date': 'Due'}
        help_texts = {'due_date': 'Date the installment is due'}
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
        }


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
