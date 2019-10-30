from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone
from django.contrib.admin.widgets import FilteredSelectMultiple
from ..widgets import DateTimePickerWidget

from ..models import Call, TemplateQuestion, CallQuestion, BudgetCategory


class CallQuestionItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('id', css_class='col-12', hidden=True),
                Div('order', css_class='col-12'),
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
            Div(
                Div('answer_max_length', css_class='col-12'),
                css_class='row'
            )
        )

    class Meta:
        model = CallQuestion
        fields = ['id', 'order', 'question_text', 'question_description', 'answer_max_length']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4}),
            'question_description': forms.Textarea(attrs={'rows': 4})
        }


class CallQuestionFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.order_by('order')

        self.helper = FormHelper()
        self.helper.form_tag = False


CallQuestionItemFormSet = inlineformset_factory(
    Call, CallQuestion, form=CallQuestionItemForm, formset=CallQuestionFormSet, extra=0,
    can_delete=False)


class CallForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # template_ids_used = CallQuestion.objects.filter(call=self.instance).values_list('question', flat=True)
            # questions_qs = TemplateQuestion.objects.exclude(id__in=template_ids_used)
            budget_categories_qs = self.instance.budget_categories.all()
            # used_questions = self.instance.call
            questions = self.instance.callquestion_set.all().values_list('template_question', flat=True)
            used_questions = TemplateQuestion.objects.filter(id__in=questions)
        else:
            budget_categories_qs = []
            used_questions = []

        self.fields['budget_categories'] = forms.ModelMultipleChoiceField(initial=budget_categories_qs,
                                                                          queryset=BudgetCategory.objects.all(),
                                                                          widget=forms.CheckboxSelectMultiple)

        self.fields['template_questions'] = forms.ModelMultipleChoiceField(initial=used_questions,
                                                                           queryset=TemplateQuestion.objects.all(),
                                                                           required=False,
                                                                           widget=FilteredSelectMultiple(is_stacked=True, verbose_name='questions'),
                                                                           help_text=self.Meta.help_texts['template_questions'])

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('funding_instrument', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('long_name', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('short_name', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('description', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('introductory_message', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('call_open_date', css_class='col-6'),
                Div('submission_deadline', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('budget_categories', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('budget_maximum', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('other_funding_question', css_class='col-6'),
                Div('proposal_partner_question', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('template_questions', css_class='col-12'),
                css_class='row'
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['call_open_date'] >= cleaned_data['submission_deadline']:
            self.add_error('call_open_date', 'Call open date needs to be before the submission deadline')

        if cleaned_data['submission_deadline'] < timezone.now():
            self.add_error('submission_deadline', 'Call submission deadline needs to be in the future')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit)

        if commit:
            template_questions_wanted = []

            for template_question in self.cleaned_data['template_questions']:
                call_question = CallQuestion.from_template(template_question)
                template_questions_wanted.append(template_question.id)

                if instance.callquestion_set.filter(template_question=template_question):
                    # This question was already added
                    continue

                call_question.call = instance
                call_question.save()

            for call_question in instance.callquestion_set.all():
                if call_question.template_question.id not in template_questions_wanted:
                    call_question.delete()

        return instance

    class Meta:
        model = Call
        fields = ['funding_instrument', 'long_name', 'short_name', 'description', 'introductory_message', 'call_open_date',
                  'submission_deadline', 'budget_categories', 'budget_maximum', 'other_funding_question', 'proposal_partner_question', ]

        field_classes = {
            'call_open_date': forms.SplitDateTimeField,
            'submission_deadline': forms.SplitDateTimeField
        }

        widgets = {
            'call_open_date': DateTimePickerWidget,
            'submission_deadline': DateTimePickerWidget
        }

        help_texts = {'description': 'Brief description of the call (for display to management only)',
                      'introductory_message': 'This text will be displayed at the top of the application form. '
                                              'It should include information required to complete the application  '
                                              'correctly such as <strong>eligibility</strong>, <strong>criteria</strong>, '
                                              '<strong>application</strong> and <strong>submission</strong>',
                      'call_open_date': 'Enter the date and time at which the call opens (Swiss time)',
                      'submission_deadline': 'Enter the date and time after which no more submissions are accepted (Swiss time)',
                      'template_questions': 'Select the questions that you would like to add to this call',
                      'other_funding_question': 'Tick this box if you would like the call to ask about other funding that will contribute to the proposal',
                      'proposal_partner_question': 'Tick this box if you would like the call to ask about proposal partners'}

        labels = {
            'budget_maximum': 'Budget maximum (CHF)'
        }