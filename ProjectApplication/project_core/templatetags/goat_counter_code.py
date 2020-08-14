from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def goat_counter_code():
    return settings.GOAT_COUNTER_CODE
