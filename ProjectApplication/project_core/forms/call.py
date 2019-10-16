from crispy_forms.helper import FormHelper
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone

from ..models import Call, TemplateQuestion, CallQuestion, BudgetCategory


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
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4}),
            'question_description': forms.Textarea(attrs={'rows': 4})
        }


class CallForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            template_ids_used = CallQuestion.objects.filter(call=self.instance).values_list('question', flat=True)
            questions_qs = TemplateQuestion.objects.exclude(id__in=template_ids_used)
            budget_categories_qs = self.instance.budget_categories.all()
        else:
            questions_qs = TemplateQuestion.objects.all()
            budget_categories_qs = []

        self.fields['template_questions'] = forms.ModelMultipleChoiceField(queryset=questions_qs, required=False,
                                                                           help_text=self.Meta.help_texts['template_questions'])

        self.fields['budget_categories'] = forms.ModelMultipleChoiceField(initial=budget_categories_qs,
                                                                          queryset=BudgetCategory.objects.all(),
                                                                          widget=forms.CheckboxSelectMultiple)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['call_open_date'] >= cleaned_data['submission_deadline']:
            self.add_error('call_open_date', 'Call open date needs to be before the submission deadline')

        if cleaned_data['submission_deadline'] < timezone.now():
            self.add_error('submission_deadline', 'Call submission deadline needs to be in the future')

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

        field_classes = {
            'call_open_date': forms.SplitDateTimeField,
            'submission_deadline': forms.SplitDateTimeField
        }

        widgets = {
            'call_open_date': DateTimePickerWidget,
            'submission_deadline': DateTimePickerWidget
        }

        help_texts = {'description': 'Brief description of the call (internal only)',
                      'introductory_message': 'This text will be displayed at the top of the application form. '
                                              'It should include information required to complete the application  '
                                              'correctly such as <b>eligibility</b>, <b>criteria</b>, '
                                              '<b>application</b> and <b>submission</b>',
                      'call_open_date': 'Enter the date and time at which the call opens (Swiss time)',
                      'submission_deadline': 'Enter the date and time after which no more submissions are accepted (Swiss time)',
                      'template_questions': 'a'}


class CallQuestionFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.order_by('order')

        self.helper = FormHelper()
        self.helper.form_tag = False


CallQuestionItemFormSet = inlineformset_factory(
    Call, CallQuestion, form=CallQuestionItemForm, formset=CallQuestionFormSet, extra=0,
    can_delete=True)
