from django import forms


class AmountField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, localize=True, **kwargs)

    def to_python(self, value):
        if value is None:
            return None

        value = str(value)
        value = value.replace("'", '')  # thousands separator
        value = value.replace("‘", '')  # typographic thousands separator
        return super().to_python(value)