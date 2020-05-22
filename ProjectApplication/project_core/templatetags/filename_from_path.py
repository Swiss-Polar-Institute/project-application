import os

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def short_filename_from_path(path):
    filename = os.path.basename(path)
    max_length = 12

    base_filename, extension = os.path.splitext(filename)

    if len(base_filename) > max_length - 3:
        if extension.startswith('.'):
            extension = extension[1:]

        filename = base_filename[:max_length] + '…' + extension

    return filename


@register.filter
@stringfilter
def filename_from_path(path):
    return os.path.basename(path)
