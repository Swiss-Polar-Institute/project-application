import os

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def filename_from_path(path):
    return os.path.basename(path)
