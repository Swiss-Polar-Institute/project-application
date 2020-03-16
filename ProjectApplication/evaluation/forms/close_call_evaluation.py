from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.urls import reverse


class CloseCallEvaluation(forms.Form):
    name = 'close_call_evaluation_form'

    def __init__(self, *args, **kwargs):
        call_id = kwargs.pop('call_id')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.form_action = reverse('logged-call-close-evaluation', kwargs={'call_id': call_id})

        self.helper.layout = Layout(
            FormActions(
                Submit('save', 'Close Evaluation'),
            )
        )
