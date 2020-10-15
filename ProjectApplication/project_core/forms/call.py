import logging
import re
from datetime import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.urls import reverse
from django.utils import timezone

from ..fields import FlexibleDecimalField
from ..models import Call, TemplateQuestion, CallQuestion, FundingInstrument, BudgetCategoryCall, BudgetCategory
from ..widgets import XDSoftYearMonthDayHourMinutePickerInput, CheckboxSelectMultipleSortable

logger = logging.getLogger('project_core')


class CallQuestionItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.fields['question_text'].widget.attrs = {'rows': 2}
        self.fields['question_description'].widget.attrs = {'rows': 2}
        self.fields['order'].label = 'Question number'

        divs = []

        divs.append(Div(
            Div('id', css_class='col-12', hidden=True),
            Div('order', css_class='col-6'),
            css_class='row')
        )

        divs.append(Div(
            Div('question_text', css_class='col-12'),
            css_class='row')
        )

        divs.append(Div(
            Div('question_description', css_class='col-12'),
            css_class='row')
        )

        if self.instance.answer_type == CallQuestion.TEXT:
            divs.append(Div(
                Div(HTML(
                    f'Answer type: {{% include  "common/_answer_type-icon.tmpl" with type="{self.instance.answer_type}" %}}'),
                    css_class='col-6'),
                Div('answer_max_length', css_class='col-6'),
                css_class='row'
            )
            )

        divs.append(Div(
            Div('answer_required', css_class='col-12'),
            css_class='row')
        )

        self.helper.layout = Div(*divs)

    class Meta:
        model = CallQuestion
        fields = ['id', 'order', 'question_text', 'question_description', 'answer_max_length', 'answer_required', ]
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4}),
            'question_description': forms.Textarea(attrs={'rows': 4})
        }
        help_texts = {
            'order': 'The question number is used to order the questions in the proposal form. Questions will be ordered in ascending order of the integer in this box.'}


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
            questions = self.instance.callquestion_set.all().values_list('template_question', flat=True)
            used_questions = TemplateQuestion.objects.filter(id__in=questions)
        else:
            self.fields['finance_year'].initial = datetime.now().year
            used_questions = []

        self.budget_categories_order_key = f'budget_categories-{CheckboxSelectMultipleSortable.order_of_values_name}'

        budget_category_choices = []
        enabled_budget_categories = []
        general_categories_added = set()

        for budget_category_call in BudgetCategoryCall.objects.filter(call=self.instance).order_by('order'):
            budget_category_choices.append(
                (budget_category_call.budget_category.id, budget_category_call.budget_category.name))
            general_categories_added.add(budget_category_call.budget_category.id)

            if budget_category_call.enabled:
                enabled_budget_categories.append(budget_category_call.budget_category.id)

        for budget_category_general in BudgetCategory.objects.all().order_by('order'):
            if budget_category_general.id not in general_categories_added:
                budget_category_choices.append((budget_category_general.id, budget_category_general.name))

        self.fields['budget_categories'] = forms.MultipleChoiceField(choices=budget_category_choices,
                                                                     initial=enabled_budget_categories,
                                                                     widget=CheckboxSelectMultipleSortable,
                                                                     )
        # queryset=BudgetCategoryCall.objects.filter(call=self.instance).order_by('order'),
        # self.fields['budget_categories'].widget = CheckboxSelectMultiple

        self.fields['template_questions'] = forms.ModelMultipleChoiceField(initial=used_questions,
                                                                           queryset=TemplateQuestion.objects.all(),
                                                                           required=False,
                                                                           widget=FilteredSelectMultiple(
                                                                               is_stacked=True,
                                                                               verbose_name='questions'),
                                                                           label=self.Meta.labels['template_questions'])

        self.fields['funding_instrument'].queryset = FundingInstrument.objects.order_by('long_name')
        self.fields['budget_categories'].label = 'Budget categories (drag and drop to sort them)'

        self.fields[
            'template_questions'].help_text = f'Select the questions that you would like to add to this call and move them to the box below using the arrow. ' \
                                              f'Check the full details of the question are correct by <a href="{reverse("logged-template-question-list")}">viewing ' \
                                              f'the template questions</a>, or <a href="{reverse("logged-template-question-add")}">create a new template ' \
                                              f'question</a> if necessary.'

        XDSoftYearMonthDayHourMinutePickerInput.set_format_to_field(self.fields['call_open_date'])
        XDSoftYearMonthDayHourMinutePickerInput.set_format_to_field(self.fields['submission_deadline'])

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
                Div('short_name', css_class='col-6'),
                Div('finance_year', css_class='col-6'),
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
                Div('budget_maximum', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('budget_categories', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('other_funding_question', css_class='col-6'),
                Div('proposal_partner_question', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('overarching_project_question', css_class='col-12'),
                css_class='row'
            ),
            Div(
                HTML('<h2 class="col-12">Questions</h2>'),
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

        data_budget_categories_order_key = f'{self.prefix}-{self.budget_categories_order_key}'

        if data_budget_categories_order_key in self.data:
            order_data = self.data[data_budget_categories_order_key]

            if order_data == '':
                self.cleaned_data[self.budget_categories_order_key] = None
            elif re.search(r'^(\d+,)*\d+$', order_data):
                # The order for the list is like '4,3,1,10' (starts with a number, has commas, ends with a number)
                self.cleaned_data[self.budget_categories_order_key] = order_data
            else:
                logger.warning(
                    f'NOTIFY: Error when parsing order of the budget categories. Received: {order_data}')

                raise ValidationError(
                    'Error when parsing order of the budget categories. Try again or contact Project Application administrators')

        else:
            self.cleaned_data[self.budget_categories_order_key] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit)

        CheckboxSelectMultipleSortable.add_missing_related_objects(BudgetCategoryCall, instance, 'call',
                                                                   BudgetCategory, 'budget_category')
        # add_missing_budget_categories_call(call=instance)

        # Marks all as do not enable
        BudgetCategoryCall.objects.filter(call=instance).update(enabled=False)

        for category_id in self.cleaned_data['budget_categories']:
            budget_category_call = BudgetCategoryCall.objects.get(call=instance, budget_category__id=category_id)
            budget_category_call.enabled = True
            budget_category_call.save()

        # Enable the ones that are enabled
        BudgetCategoryCall.objects.filter(call=instance).filter(
            budget_category__in=self.cleaned_data['budget_categories']).update(enabled=True)

        CheckboxSelectMultipleSortable.save_order(BudgetCategoryCall, instance, 'call', 'budget_category',
                                                  self.cleaned_data.get(self.budget_categories_order_key, None))

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
        fields = ['funding_instrument', 'long_name', 'short_name', 'finance_year', 'description',
                  'introductory_message',
                  'call_open_date', 'submission_deadline', 'budget_maximum',
                  'other_funding_question', 'proposal_partner_question', 'overarching_project_question', ]

        field_classes = {'budget_maximum': FlexibleDecimalField}

        widgets = {
            'call_open_date': XDSoftYearMonthDayHourMinutePickerInput,
            'submission_deadline': XDSoftYearMonthDayHourMinutePickerInput,
        }

        help_texts = {'description': 'Brief description of the call (for display to management only)',
                      'introductory_message': 'This text will be displayed at the top of the application form. '
                                              'It should include information required to complete the application  '
                                              'correctly such as <strong>eligibility</strong>, <strong>criteria</strong>, '
                                              '<strong>application</strong> and <strong>submission</strong>',
                      'call_open_date': 'Enter the date and time at which the call opens (Swiss time)',
                      'submission_deadline': 'Enter the date and time after which no more submissions are accepted (Swiss time)',
                      'other_funding_question': 'Tick this box if you would like the call to ask about other funding that will contribute to the proposal',
                      'proposal_partner_question': 'Tick this box if you would like the call to ask about proposal partners',
                      'overarching_project_question': 'Tick this box if you would like the call to ask about the overarching project'}

        labels = {
            'budget_maximum': 'Budget maximum (CHF)',
            'template_questions': ''
        }
