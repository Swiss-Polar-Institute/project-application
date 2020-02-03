from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='user_is_management')
def user_is_management(request):
    try:
        request.user.groups.get(name='management')
        return True
    except ObjectDoesNotExist:
        return False
