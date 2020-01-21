from project_core.models import Call
from .models import CallVariableTemplate


def copy_template_variables_from_funding_instrument_to_call(call : Call):
    for template_variable in call.funding_instrument.fundinginstrumentvariabletemplate_set.all():
        call_template_variable = CallVariableTemplate(call=call,
                                                      name=template_variable.name,
                                                      value=template_variable.value)
        call_template_variable.save()
