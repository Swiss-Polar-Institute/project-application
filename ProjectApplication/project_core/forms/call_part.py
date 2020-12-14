from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.urls import reverse

from .utils import cancel_edit_button
from ..models import FinancialKey, CallPart, Call


class CallPartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        call_pk = kwargs.pop('call_pk')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        if kwargs['instance']:
            action_text = 'Save Call Part'
            cancel_url = reverse('logged-call-part-detail',
                                 kwargs={'call_pk': call_pk, 'proposal_part_pk': kwargs['instance'].id})
        else:
            action_text = 'Create Call Part'
            cancel_url = reverse('logged-call-detail',
                                 kwargs={'pk': call_pk})

        self.fields['call'].initial = Call.objects.get(pk=call_pk)

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

    class Meta:
        model = CallPart
        fields = ['call', 'order', 'title', 'introductory_text', ]
