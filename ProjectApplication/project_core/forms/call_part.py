import bleach
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.db.models import Max
from django.urls import reverse

from .utils import cancel_edit_button
from ..models import CallPart, Call


class CallPartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        call_pk = kwargs.pop('call_pk')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        if kwargs['instance']:
            action_text = 'Save Call Part'
            cancel_url = reverse('logged-call-part-detail',
                                 kwargs={'call_pk': call_pk, 'call_part_pk': kwargs['instance'].id})
        else:
            action_text = 'Create Call Part'
            cancel_url = reverse('logged-call-detail',
                                 kwargs={'pk': call_pk})

        self.fields['call'].initial = Call.objects.get(pk=call_pk)
        self._call = self.fields['call'].initial

        self.helper.layout = Layout(
            Div(
                Div('call', css_class='col-12', hidden=True),
                css_class='row'
            ),
            Div(
                Div('order', css_class='col-3'),
                css_class='row'
            ),
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('introductory_text', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', action_text),
                cancel_edit_button(cancel_url)
            )
        )

    def clean_introductory_text(self):
        data = self.cleaned_data['introductory_text']

        data = bleach.clean(bleach.linkify(data, parse_email=True))

        return data

    def clean_order(self):
        if self.cleaned_data['order'] is None:
            last_order = CallPart.objects.filter(call=self._call).aggregate(Max('order'))
            order_max = last_order['order__max']

            return order_max+10 if order_max else 10
        else:
            return self.cleaned_data['order']

    class Meta:
        model = CallPart
        fields = ['call', 'order', 'title', 'introductory_text', ]
        help_texts = {'order': 'If left blank it will be the last one',
                      'introductory_text': 'It allows HTML'}