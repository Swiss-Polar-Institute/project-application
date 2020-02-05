from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist

from project_core.models import Call
from variable_templates.models import CallVariableTemplate, TemplateVariableName, FundingInstrumentVariableTemplate


def copy_template_variables_from_funding_instrument_to_call(call: Call):
    for template_variable in call.funding_instrument.fundinginstrumentvariabletemplate_set.all():
        call_template_variable = CallVariableTemplate(call=call,
                                                      name=template_variable.name,
                                                      value=template_variable.value)
        call_template_variable.save()


def apply_templates(fields: OrderedDict, call):
    # Replaces the {{ name }}
    template_name_values = {}

    for template_name_value in TemplateVariableName.objects.all():
        template_name_values[template_name_value.name] = template_name_value.default

    for template_name_value in FundingInstrumentVariableTemplate.objects.filter(
            funding_instrument=call.funding_instrument):
        template_name_values[template_name_value.name.name] = template_name_value.value

    for template_name_value in CallVariableTemplate.objects.filter(call=call).all():
        template_name_values[template_name_value.name.name] = template_name_value.value

    for field in fields.items():
        for template_name in template_name_values.keys():
            if field[1].label:
                field[1].label = field[1].label.replace(f'{{{{ {template_name} }}}}',
                                                        template_name_values[template_name])
            if field[1].help_text:
                field[1].help_text = field[1].help_text.replace(f'{{{{ {template_name} }}}}',
                                                                template_name_values[template_name])


def get_template_value(name, call):
    # Returns the template value of the template name for call or the default
    try:
        template_variable_name = CallVariableTemplate.objects.get(call=call, name__name=name)
        value = template_variable_name.value
        return value

    except ObjectDoesNotExist:
        pass

    try:
        template_variable_name = TemplateVariableName.objects.get(name=name)
        value = template_variable_name.default
        return value
    except ObjectDoesNotExist:
        pass

    assert False
