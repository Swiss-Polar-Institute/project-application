from django import template

from ProjectApplication import settings
from project_core.utils import user_is_in_group_name

register = template.Library()


@register.filter(name='request_is_management')
def request_is_management(request):
    return user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME)
