from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='request_is_reviewer')
def request_is_reviewer(request):
    return user_is_reviewer(request.user)


def user_is_reviewer(user):
    try:
        user.groups.get(name='reviewer')
        return True
    except ObjectDoesNotExist:
        return False
