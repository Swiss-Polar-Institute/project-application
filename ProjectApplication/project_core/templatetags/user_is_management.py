from django import template

register = template.Library()


@register.filter(name='user_is_management')
def is_management(user):
    return user.groups.filter(name='management').exists()
