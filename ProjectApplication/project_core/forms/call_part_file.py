from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.db.models import Max
from django.urls import reverse

from .utils import cancel_button
from ..models import CallPart, CallPartFile


class CallPartFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        call_part_pk = kwargs.pop('call_part_pk')

        super().__init__(*args, **kwargs)

        self._call_part = CallPart.objects.get(pk=call_part_pk)

        self.helper = FormHelper(self)

        if kwargs['instance']:
            action_text = 'Save File'
        else:
            action_text = 'Create File'

        cancel_url = reverse('logged-call-detail', kwargs={'pk': self._call_part.call.pk}) + '#parts'

        self.fields['call_part'].initial = self._call_part

        self.helper.layout = Layout(
            Div(
                Div('call_part', css_class='col-12', hidden=True),
                css_class='row'
            ),
            Div(
                Div('name', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('description', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('file', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('order', css_class='col-3'),
                css_class='row'
            ),
            FormActions(
                Submit('save', action_text),
                cancel_button(cancel_url)
            )
        )

    def clean_order(self):
        if self.cleaned_data['order'] is None:
            last_order = CallPartFile.objects.filter(call_part=self._call_part).aggregate(Max('order'))[
                             'order__max'] or 0
            return last_order + 10
        else:
            return self.cleaned_data['order']

    class Meta:
        model = CallPartFile
        fields = ['call_part', 'name', 'description', 'order', 'file', ]
