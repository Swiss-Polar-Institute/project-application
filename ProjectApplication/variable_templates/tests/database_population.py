from ..models import TemplateVariableName, FundingInstrumentVariableTemplate, CallVariableTemplate


def delete_all_variables():
    TemplateVariableName.objects.all().delete()
    FundingInstrumentVariableTemplate.objects.all().delete()
    CallVariableTemplate.objects.all().delete()


def create_default_template_variables():
    TemplateVariableName.objects.get_or_create(name='activity', default='proposal')
