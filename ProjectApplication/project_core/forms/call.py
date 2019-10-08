from django import forms

from ..models import Call, TemplateQuestion, CallQuestion
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from crispy_forms.helper import FormHelper


class DateTimePickerWidget(forms.SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         date_attrs={'type': 'date'},
                         time_attrs={'type': 'time'}
                         )


class CallQuestionItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = CallQuestion
        fields = ['id', 'order', 'question_text', 'question_description', 'answer_max_length']


class CallForm(forms.ModelForm):
    call_open_date = forms.SplitDateTimeField(widget=DateTimePickerWidget)
    submission_deadline = forms.SplitDateTimeField(widget=DateTimePickerWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            template_ids_used = CallQuestion.objects.filter(call=self.instance).values_list('question', flat=True)
            questions_qs = TemplateQuestion.objects.exclude(id__in=template_ids_used)
        else:
            questions_qs = TemplateQuestion.objects.all()

        self.fields['template_questions'] = forms.ModelMultipleChoiceField(queryset=questions_qs, required=False,
                                                                           help_text='Templates not used in this call')

        self.helper = FormHelper(self)
        self.helper.form_tag = False


    def save(self, commit=True):
        instance = super().save(commit)

        if commit:
            for question in self.cleaned_data['template_questions']:
                call_question = CallQuestion.from_template(question)
                call_question.call = instance
                call_question.save()

        return instance

    class Meta:
        model = Call
        fields = ['long_name', 'short_name', 'description', 'introductory_message', 'call_open_date',
                  'submission_deadline', 'budget_categories', 'budget_maximum', ]


class CallQuestionFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.order_by('order')

        self.helper = FormHelper()
        self.helper.form_tag = False


CallQuestionItemFormSet = inlineformset_factory(
    Call, CallQuestion, form=CallQuestionItemForm, formset=CallQuestionFormSet, extra=0,
    can_delete=True)
