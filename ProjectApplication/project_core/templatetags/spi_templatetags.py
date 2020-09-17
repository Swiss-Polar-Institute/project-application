from django import template

from django.template.defaultfilters import linebreaksbr

register = template.Library()

@register.filter(name='spi_linebreaksbr')
def spi_linebreaksbr(value):
    ''' The Django linebreaksbr converts None to a TextSafe 'None' string. This one returns
    None is value is None
    '''
    if value is None:
        return None

    return linebreaksbr(value)