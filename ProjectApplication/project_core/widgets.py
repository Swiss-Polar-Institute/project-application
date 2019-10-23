from django import forms


class DateTimePickerWidget(forms.SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         date_attrs={'type': 'date'},
                         time_attrs={'type': 'time'}
                         )


class DatePickerWidget(forms.DateInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, attrs={'type': 'date'})
