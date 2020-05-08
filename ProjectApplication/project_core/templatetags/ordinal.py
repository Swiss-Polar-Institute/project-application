from django import template
from django.contrib.humanize.templatetags.humanize import ordinal as humanize_ordinal

register = template.Library()


@register.filter(name='ordinal')
def ordinal(value):
    if value is None:
        return None

    humanized = {1: 'First',
                 2: 'Second',
                 3: 'Third',
                 4: 'Fourth',
                 5: 'Fifth',
                 6: 'Sixth',
                 7: 'Seventh',
                 8: 'Eighth',
                 9: 'Ninth',
                 10: 'Tenth'}

    if value in humanized:
        return humanized[value]
    else:
        return humanize_ordinal(value)
