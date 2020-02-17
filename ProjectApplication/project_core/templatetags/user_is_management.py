from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='request_is_management')
def request_is_management(request):
    return user_is_management(request.user)


def user_is_management(user):
    try:
        user.groups.get(name='management')
        return True
    except ObjectDoesNotExist:
        return False
