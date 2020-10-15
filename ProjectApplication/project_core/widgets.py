from django import forms
from django.forms import DateTimeInput, DateInput
from django.forms.widgets import ChoiceWidget

from evaluation.models import CriterionCallEvaluation
from project_core.models import BudgetCategoryCall


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
    # See https://djangosnippets.org/snippets/1053/
    allow_multiple_selected = True
    input_type = 'checkbox'
    template_name = 'widgets/_select_multiple_sortable.tmpl'
    order_of_values_name = 'order_of_values'

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

    def value_from_datadict(self, data, files, name):
        return super().value_from_datadict(data, files, name)

    @staticmethod
    def save_order_call_budget_categories(call, order_data):
        # This should not be here and should be automatic for the users of this Widget
        # TODO: make it automatic

        order = 1
        for category in order_data.split(','):
            budget_category_call, created = BudgetCategoryCall.objects.get_or_create(call=call,
                                                                                     budget_category_id=category,
                                                                                     defaults={'enabled': False})
            budget_category_call.order = order
            budget_category_call.save()

            order += 1

    @staticmethod
    def save_order_criterion_evaluation_categories(call_evaluation, order_data):
        # This should not be here and should be automatic for the users of this Widget
        # TODO: make it automatic

        order = 1
        for criterion_id in order_data.split(','):
            criterion_call_evaluation, created = CriterionCallEvaluation.objects.get_or_create(
                call_evaluation=call_evaluation,
                criterion_id=criterion_id,
                defaults={'enabled': False})
            criterion_call_evaluation.order = order
            criterion_call_evaluation.save()

            order += 1
