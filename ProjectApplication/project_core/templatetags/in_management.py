from django import template

register = template.Library()


@register.filter(name='in_management')
def in_management(request):
    return request and request.path.startswith('/management/')
