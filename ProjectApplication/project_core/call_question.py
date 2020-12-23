from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse

from project_core.forms.utils import cancel_edit_button
from project_core.models import CallQuestion, CallPart


class CallQuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        if self.instance.pk:
            cancel_edit_url = reverse('logged-call-question-detail',
                                         kwargs={'call_pk': self.instance.call_part.call.pk,
                                                 'call_question_pk': self.instance.pk
                                                 })
            self.fields['call_part'].queryset = CallPart.objects.filter(call=self.instance.call_part.call)

        else:
            assert False

        self.helper.layout = Layout(
            Div(
                Div('call_part', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('question_text', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('question_description', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Call Question'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    class Meta:
        model = CallQuestion
        fields = ['call_part', 'question_text', 'question_description']
        widgets = {'question_text': forms.TextInput}
