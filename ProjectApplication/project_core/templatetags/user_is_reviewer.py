from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='user_is_reviewer')
def user_is_reviewer(request):
    try:
        request.user.groups.get(name='reviewer')
        return True
    except ObjectDoesNotExist:
        return False
