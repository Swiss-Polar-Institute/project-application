from django import forms
from django.forms import DateTimeInput, DateInput


class DateTimePickerWidget(forms.SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         date_attrs={'type': 'date'},
                         time_attrs={'type': 'time'}
                         )


class DatePickerWidget(forms.DateInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, attrs={'type': 'date'})


class XDSoftYearMonthDayHourMinutePickerInput(DateTimeInput):
    def __init__(self, *args, **kwargs):
        # This widget supports only a fixed format (also specified in the .tmpl file)
        assert 'format' not in kwargs
        kwargs['format'] = '%d-%m-%Y %H:%M'
        super().__init__(*args, **kwargs)

    template_name = 'widgets/xdsoft_year_month_day_hour_minute_picker.tmpl'


class XDSoftYearMonthDayPickerInput(DateInput):
    def __init__(self, *args, **kwargs):
        # This widget supports only a fixed format (also specified in the .tmpl file)
        assert 'format' not in kwargs
        kwargs['format'] = '%d-%m-%Y'
        super().__init__(*args, **kwargs)

    template_name = 'widgets/xdsoft_year_month_day_picker.tmpl'


class XDSoftYearMonthPickerInput(DateInput):
    def __init__(self, *args, **kwargs):
        # This widget supports only a fixed format (also specified in the .tmpl file)
        assert 'format' not in kwargs
        kwargs['format'] = '%m-%Y'
        super().__init__(*args, **kwargs)

    template_name = 'widgets/xdsoft_year_month_picker.tmpl'
