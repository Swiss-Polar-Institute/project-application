from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
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
    def save_order(model, parent_object, parent_object_field: str, related_object_field: str, order_data):
        if order_data is None:
            return

        order = 1

        for related_object_id in order_data.split(','):
            filter = {parent_object_field: parent_object,
                      f'{related_object_field}_id': related_object_id}

            item, created = model.objects.get_or_create(**filter, defaults={'enabled': False})
            item.order = order
            item.save()

            order += 1

    @staticmethod
    def add_missing_related_objects(model, parent_object, parent_object_field: str, related_model,
                                    related_object_field: str):
        all_related_model_ids = related_model.objects.all().values_list('id', flat=True)
        current_object_ids = model.objects.filter(**{parent_object_field: parent_object}).values_list(
            f'{related_object_field}_id', flat=True)

        missing_ids = set(all_related_model_ids) - set(current_object_ids)

        # New items added at the bottom - consistent with how they are displayed
        current_maximum = model.objects. \
            filter(**{parent_object_field: parent_object}). \
            aggregate(Max('order'))['order__max']

        if current_maximum is None:
            current_maximum = 1

        for missing_id in missing_ids:
            try:
                item = related_model.objects.get(id=missing_id)
            except ObjectDoesNotExist:
                # This category has been deleted between the time that the form was presented to now
                continue

            current_maximum += 1
            model.objects.create(**{parent_object_field: parent_object,
                                    f'{related_object_field}_id': missing_id,
                                    'enabled': False,
                                    'order': current_maximum})

    @staticmethod
    def save_enabled_disabled(model, parent_model, parent_object, parent_object_field: str, related_object_field: str,
                              enabled_ids):
        model.objects.filter(**{parent_object_field: parent_object}).update(enabled=False)

        for related_object_id in enabled_ids:
            object = model.objects.get(**{parent_object_field: parent_object,
                                          f'{related_object_field}_id': related_object_id})
            object.enabled = True
            object.save()

        # CriterionCallEvaluation.objects.filter(call_evaluation=call_evaluation).update(enabled=False)
        #
        # # Enabled the correct ones
        # for criterion_id in self.cleaned_data['criteria']:
        #     criterion_call_evaluation = CriterionCallEvaluation.objects.get(call_evaluation=call_evaluation,
        #                                                                     criterion_id=criterion_id)
        #     criterion_call_evaluation.enabled = True
        #     criterion_call_evaluation.save()
