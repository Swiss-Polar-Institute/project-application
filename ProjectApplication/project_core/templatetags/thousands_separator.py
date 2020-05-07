from django import template

register = template.Library()


@register.filter(name='thousands_separator')
def thousands_separator(value):
    """
    Using settings.THOUSANDS_SEPARATOR generic way has two problems:
    a) it then is not possible to use DATE_FORMAT as we want
    b) all the numbers have thousand separators not only amounts
    """
    if value is None:
        return None

    value = float(value)
    return f'{value:_.2f}'.replace('_', "'")
