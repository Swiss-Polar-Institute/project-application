from ..models import TemplateVariableName

def create_default_variables():
    TemplateVariableName.objects.get_or_create(name='activity', default='proposal')