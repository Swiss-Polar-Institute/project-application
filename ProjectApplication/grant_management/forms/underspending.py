from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.safestring import mark_safe

from grant_management.forms.invoices import html_message
from grant_management.models import Underspending
from project_core.fields import FlexibleDecimalField
from project_core.models import Project
from project_core.templatetags.thousands_separator import thousands_separator


class UnderspendingsModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        message = ''
        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)

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

        if project.is_active() is False:
            raise ValidationError(f'Cannot modify underspending for this project: the status is {project.status}')

        return cd

    class Meta:
        model = Underspending
        fields = ['project', 'amount']
        field_classes = {'amount': FlexibleDecimalField}
        labels = {'amount': 'Amount (CHF)'}


class UnderspendingsFormSet(BaseInlineFormSet):
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


    def get_queryset(self):
        return super().get_queryset().order_by('id')

    def extra_information(self):
        return mark_safe(f'<p><b>Budget allocated</b>: {thousands_separator(self.instance.allocated_budget)} CHF</p>')


UnderspendingsInlineFormSet = inlineformset_factory(Project, Underspending, form=UnderspendingsModelForm,
                                                  formset=UnderspendingsFormSet,
                                                  min_num=1, extra=0, can_delete=True)
