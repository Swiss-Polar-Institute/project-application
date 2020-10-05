from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput


class FlexibleDecimalField(forms.DecimalField):
    # It has a few features:
    # treats ' and ‘ as thousand separators (in practically they are ignored before parsing the number)
    # treats '.' and ',' as decimal separators and forces maximum two decimal fields. Makes sure that there
    # are in the "correct" place: at the end of the string
    def __init__(self, *args, **kwargs):
        # DecimalField inherits of IntegerField. In the constructor of IntegerField if localize=False
        # it uses a numeric HTML widget (easy to see: it has the arrows up and down... and it accepts either
        # '.' or ',' depending on the browser's locale for the comma separation. Doing this we force to use a
        # TextInput: the FlexibleDecimalField cannot use a NumericWidget because the browser validation is too strict
        # (regarding , and .)
        # We could complement this with Javascript code to validate in our case (and validate again in the server)
        # for simplicity we are doing it on the server side only.
        # Users of FlexibleDecimalField can set the widget with the attributes that they wish.
        if 'widget' not in kwargs:
            kwargs['widget'] = TextInput()

        super().__init__(*args, **kwargs)

    def clean(self, value):

        if type(value) == str:
            # From unit tests the value can be an integer or other types
            # Here I'm consistent with what Decimal.clean() does: it doesn't fail
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
