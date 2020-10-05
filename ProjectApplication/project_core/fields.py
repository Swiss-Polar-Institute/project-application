from django import forms
from django.core.exceptions import ValidationError


class SpiNumberField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, localize=True, **kwargs)

    def clean(self, value):
        if value.count(',') > 1:
            raise ValidationError('Invalid number: it contains too many commas (,)', code='invalid')

        if value.count(',') == 1 and len(value) - 2 > value.index(',') + 1:
            # , is a decimal separator and we only accept one or two decimals. If it's not at the end of the
            # string it is an error. The user might have tried to use ',' as a thousands separator
            raise ValidationError('Please use comma (,) to separate decimals and write maximum one or two decimals')

        value = value.replace(",", '.') # some users use "," to separate decimals

        value = value.replace("'", '')  # thousands separator
        value = value.replace("‘", '')  # typographic thousands separator

        return super().clean(value)
