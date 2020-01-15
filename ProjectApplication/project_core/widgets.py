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
        kwargs['format'] = XDSoftYearMonthDayHourMinutePickerInput.format
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_format_to_field(field):
        field.input_formats = [XDSoftYearMonthDayHourMinutePickerInput.format]
        field.widget.format = XDSoftYearMonthDayHourMinutePickerInput.format

    format = '%d-%m-%Y %H:%M'
    template_name = 'widgets/xdsoft_year_month_day_hour_minute_picker.tmpl'


class XDSoftYearMonthDayPickerInput(DateInput):
    def __init__(self, *args, **kwargs):
        # This widget supports only a fixed format (also specified in the .tmpl file)
        assert 'format' not in kwargs
        kwargs['format'] = XDSoftYearMonthDayPickerInput.format
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_format_to_field(field):
        field.input_formats = [XDSoftYearMonthDayPickerInput.format]
        field.widget.format = XDSoftYearMonthDayPickerInput.format

    format = '%d-%m-%Y'
    template_name = 'widgets/xdsoft_year_month_day_picker.tmpl'


class XDSoftYearMonthPickerInput(DateInput):
    def __init__(self, *args, **kwargs):
        # This widget supports only a fixed format (also specified in the .tmpl file)
        assert 'format' not in kwargs
        kwargs['format'] = XDSoftYearMonthPickerInput.format
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_format_to_field(field):
        field.input_formats = [XDSoftYearMonthPickerInput.format]
        field.widget.format = XDSoftYearMonthPickerInput.format

    format = '%m-%Y'
    template_name = 'widgets/xdsoft_year_month_picker.tmpl'
