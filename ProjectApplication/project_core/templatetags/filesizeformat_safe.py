import botocore
from django import template
from django.template.defaultfilters import filesizeformat

register = template.Library()


@register.filter(name='filesizeformat_safe')
def filesizeformat_safe(filefield):
    try:
        size = filefield.size
    except botocore.exceptions.ClientError:
        return 'File not found'

    return filesizeformat(size)
