from django import forms

from ..models import Call


class DateTimePickerWidget(forms.SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         date_attrs={'type': 'date'},
                         time_attrs={'type': 'time'}
                         )


class CallForm(forms.ModelForm):
    call_open_date = forms.SplitDateTimeField(widget=DateTimePickerWidget)
    submission_deadline = forms.SplitDateTimeField(widget=DateTimePickerWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Call
        fields = ['long_name', 'short_name', 'description', 'introductory_message', 'call_open_date',
                  'submission_deadline', 'budget_categories', 'budget_maximum', ]
