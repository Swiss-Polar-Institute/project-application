from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Max
from django.urls import reverse

from project_core.forms.utils import cancel_edit_button
from project_core.models import CallQuestion, CallPart, TemplateQuestion


class CallQuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._call_part_pk = kwargs.pop('call_part_pk', None)

        super().__init__(*args, **kwargs)

        assert self.instance.pk or self._call_park_pk

        self.helper = FormHelper(self)

        if self.instance.pk:
            cancel_edit_url = reverse('logged-call-question-detail',
                                      kwargs={'call_pk': self.instance.call_part.call.pk,
                                              'call_question_pk': self.instance.pk
                                              })
            self.fields['call_part'].queryset = CallPart.objects.filter(call=self.instance.call_part.call)
            call = self.instance.call_part.call

        else:
            call_part = CallPart.objects.get(pk=self._call_part_pk)
            call = call_part.call
            cancel_edit_url = reverse('logged-call-update', kwargs={'pk': call_part.call.pk})
            cancel_edit_url += "#parts"

            self.fields['call_part'].initial = call_part

        self.fields['call_part'].queryset = CallPart.objects.filter(call=call)

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

    # def save(self, commit=True):
    #     return super().save(commit=commit)
    #
    class Meta:
        model = CallQuestion
        fields = ['call_part', 'question_text', 'question_description']
        widgets = {'question_text': forms.TextInput}


class CallQuestionFromTemplateQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        call_part_pk = kwargs.pop('call_part_pk')

        super().__init__(*args, **kwargs)

        self._call_part = CallPart.objects.get(pk=call_part_pk)

        used_templates = []

        for call_question in self._call_part.callquestion_set.all():
            used_templates.append(call_question.template_question)

        self.fields['template_questions'] = forms.ModelMultipleChoiceField(initial=used_templates,
                                                                           queryset=TemplateQuestion.objects.all(),
                                                                           required=False,
                                                                           widget=FilteredSelectMultiple(
                                                                               is_stacked=True,
                                                                               verbose_name='questions'),
                                                                           label='Template questions')

        cancel_edit_url = reverse('logged-call-update', kwargs={'pk': self._call_part.call.pk})
        cancel_edit_url += "#parts"

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(
                Div('template_questions', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Template Questions'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    def save(self):
        template_questions_wanted = []

        for template_question in self.cleaned_data['template_questions']:
            call_question = CallQuestion.from_template(template_question)
            template_questions_wanted.append(template_question.id)

            if self._call_part.callquestion_set.filter(template_question=template_question).exists():
                # This question was already added
                continue

            call_question.call_part = self._call_part

            last_order = CallQuestion.objects.filter(call_part=self._call_part).aggregate(Max('order'))['order__max']

            last_order = last_order + 1 if last_order else 1

            call_question.order = last_order + 1

            call_question.save()

        for call_question in self._call_part.callquestion_set.all():
            if call_question.template_question.id not in template_questions_wanted:
                call_question.delete()
