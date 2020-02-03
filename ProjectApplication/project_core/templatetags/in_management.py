from django import template

register = template.Library()
from django.conf import settings


@register.filter(name='in_management')
def in_management(request):
    return request and request.path.startswith(settings.LOGIN_REDIRECT_URL)
