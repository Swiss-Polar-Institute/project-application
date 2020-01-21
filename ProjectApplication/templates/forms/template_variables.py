from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import BaseFormSet, formset_factory

from project_core.forms.utils import PlainTextWidget
from ..models import FundingInstrument
from ..models import TemplateVariableName, FundingInstrumentVariableTemplate


class FundingInstrumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = FundingInstrument
        fields = ['long_name', 'short_name', 'description']


class TemplateVariableItemForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    name = forms.CharField(widget=PlainTextWidget())
    value = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_valid()

        template_variable = self.initial.pop('template_variable')

        self.fields['name'].help_text = f'{template_variable.name} ({template_variable.description})'
        self.fields['name'].initial = template_variable

        self.fields['value'].initial = self.initial['current_value']

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    def is_valid(self):
        return super().is_valid()

    def save_template_variable(self, funding_instrument):
        FundingInstrumentVariableTemplate.objects.update_or_create(funding_instrument=funding_instrument,
                                                                   name_id=self.cleaned_data['name'],
                                                                   defaults={'value': self.cleaned_data['value']}
                                                                   )


class TemplateVariableFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        funding_instrument = kwargs.pop('funding_instrument', None)

        initial_templates = []
        for template_variable in TemplateVariableName.objects.all():
            try:
                funding_instrument_value = FundingInstrumentVariableTemplate.objects.get(
                    funding_instrument=funding_instrument,
                    name=template_variable)
                existing_value = funding_instrument_value.value
            except ObjectDoesNotExist:
                existing_value = template_variable.default

            initial_templates.append({'id': template_variable.id,
                                      'template_variable': template_variable,
                                      'current_value': existing_value
                                      }
                                     )

        kwargs['initial'] = initial_templates

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    def is_valid(self):
        return super().is_valid()

    def save_into_funding_instrument(self, funding_instrument):
        for form in self.forms:
            form.save_template_variable(funding_instrument)


TemplateVariableItemFormSet = formset_factory(TemplateVariableItemForm, formset=TemplateVariableFormSet,
                                              can_delete=False, extra=0)
