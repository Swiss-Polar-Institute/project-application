from django import forms
from django.core.exceptions import ValidationError


class FlexibleDecimalField(forms.DecimalField):
    # It has a few features:
    # treats ' and ‘ as thousand separators (in practically they are ignored before parsing the number)
    # treats '.' and ',' as decimal separators and forces maximum two decimal fields. Makes sure that there
    # are in the "correct" place: at the end of the string
    def __init__(self, *args, **kwargs):
        super().__init__(*args, localize=True, **kwargs)

    def clean(self, value):
        if value.count(',') > 1:
            raise ValidationError('Invalid number: it contains too many commas (,)')

        if value.count('.') > 1:
            raise ValidationError('Invalid number: it contains too many full stops (.)')

        if value.count('.') == 1 and value.count(',') == 1:
            raise ValidationError('Invalid number: do not mix commas (,) and full stops (.) in the same number')

        value = value.replace(",", '.')  # some users use "," to separate decimals

        if value.count('.') == 1 and len(value) - 2 > value.index('.') + 1:
            # ',' or '.' are decimal separators and we only accept one or two decimals. If it's not at the end of the
            # string it is an error. The user might have tried to use ',' or '.' as a thousands separator
            raise ValidationError(
                'Please use comma (,) or full stops (.) to separate decimals and write maximum one or two decimals')

        value = value.replace("'", '')  # thousands separator
        value = value.replace("‘", '')  # typographic thousands separator

        return super().clean(value)
