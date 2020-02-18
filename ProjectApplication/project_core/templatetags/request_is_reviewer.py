from django import template

from ProjectApplication import settings
from project_core.utils import user_is_in_group_name

register = template.Library()


@register.filter(name='request_is_reviewer')
def request_is_reviewer(request):
    return user_is_in_group_name(request.user, settings.REVIEWER_GROUP_NAME)
