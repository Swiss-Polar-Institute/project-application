from django import forms

from ..models import Question


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ['question_text', 'question_description', 'answer_max_length']
