from django import forms
from django.forms import DateTimeInput, DateInput
from django.forms.widgets import ChoiceWidget


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


class CheckboxSelectMultipleSortable(ChoiceWidget):
    allow_multiple_selected = True
    input_type = 'checkbox'
    template_name = 'widgets/_select_multiple_sortable.tmpl'

    def use_required_attribute(self, initial):
        # Don't use the 'required' attribute because browser validation would
        # require all checkboxes to be checked instead of at least one.
        return False

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False

    def id_for_label(self, id_, index=None):
        """"
        Don't include for="field_0" in <label> because clicking such a label
        would toggle the first checkbox.
        """
        if index is None:
            return ''
        return super().id_for_label(id_, index)
