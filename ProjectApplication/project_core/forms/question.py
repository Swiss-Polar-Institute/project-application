from django import forms

from ..models import TemplateQuestion
from crispy_forms.helper import FormHelper


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = TemplateQuestion
        fields = ['question_text', 'question_description', 'answer_max_length']
