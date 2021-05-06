import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML
from django import forms
from django.db import transaction
from django.forms import CheckboxSelectMultiple

from ..fields import FlexibleDecimalField
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone

from ..models import Call, CallQuestion, FundingInstrument, BudgetCategoryCall, BudgetCategory, \
    CallPart, CallCareerStage, CareerStage
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
    CallPart, CallQuestion, form=CallQuestionItemForm, formset=CallQuestionFormSet, extra=0,
    can_delete=False)


def get_career_stages_ids_names(call):
    career_stages_ids_names = []
    enabled_ids = []

    for career_stage in CareerStage.objects.all().order_by('list_order', 'name'):
        career_stages_ids_names.append((career_stage.id, career_stage.name))
        enabled_ids.append(career_stage.id)

    if call.id:
        enabled_ids = []
        for call_career_stage in CallCareerStage.objects.filter(call=call).filter(enabled=True):
            enabled_ids.append(call_career_stage.career_stage.id)

    return career_stages_ids_names, enabled_ids


class CallForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.budget_categories_order_key = f'budget_categories-{CheckboxSelectMultipleSortable.order_of_values_name}'

        budget_category_choices, enabled_budget_categories = CheckboxSelectMultipleSortable.get_choices_initial(
            BudgetCategoryCall,
            self.instance, 'call',
            BudgetCategory, 'budget_category')

        self.fields['budget_categories'] = forms.MultipleChoiceField(choices=budget_category_choices,
                                                                     initial=enabled_budget_categories,
                                                                     widget=CheckboxSelectMultipleSortable,
                                                                     required=False
                                                                     )

        career_stages_ids_names, initial_career_stages_ids = get_career_stages_ids_names(self.instance)

        self.fields['career_stages'] = forms.MultipleChoiceField(choices=career_stages_ids_names,
                                                                 initial=initial_career_stages_ids,
                                                                 widget=CheckboxSelectMultiple,
                                                                 required=True)

        self.fields['funding_instrument'].queryset = FundingInstrument.objects.order_by('long_name')
        self.fields['budget_categories'].label = 'Budget categories (drag and drop to order them)'

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
                Div('career_stages', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('other_funding_question', css_class='col-6'),
                Div('proposal_partner_question', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('overarching_project_question', css_class='col-6'),
                Div('scientific_clusters_question', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('keywords_in_general_information_question', css_class='col-6'),
                Div('overall_budget_question', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div(HTML('<h2><a id="parts">Call Parts</a></h2>'
                         '{% include "logged/_call-part-list.tmpl" with parts=parts call=call only %}'),
                    css_class='col-12'),
                css_class='row'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['call_open_date'] >= cleaned_data['submission_deadline']:
            self.add_error('call_open_date', 'Call open date needs to be before the submission deadline')

        if cleaned_data['submission_deadline'] < timezone.now():
            self.add_error('submission_deadline', 'Call submission deadline needs to be in the future')

        data_budget_categories_order_key = f'{self.prefix}-{self.budget_categories_order_key}'

        self.cleaned_data[self.budget_categories_order_key] = CheckboxSelectMultipleSortable.get_clean_order(self.data,
                                                                                                             data_budget_categories_order_key)

        if not cleaned_data['budget_categories'] and not cleaned_data['overall_budget_question']:
            self.add_error('budget_categories',
                           'Categories are mandatory if "request overall budget question" is disabled')
        elif cleaned_data['overall_budget_question'] and cleaned_data['budget_categories']:
            self.add_error('overall_budget_question',
                           'Overall budget question cannot be enabled if there are budget categories enabled')

        if self.cleaned_data['budget_maximum'] == 0:
            self.add_error('budget_maximum', 'Budget maximum cannot be 0')

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            instance = super().save(commit)

            CheckboxSelectMultipleSortable.save(BudgetCategoryCall, instance, 'call', BudgetCategory, 'budget_category',
                                                self.cleaned_data['budget_categories'],
                                                self.cleaned_data[self.budget_categories_order_key])

            CallCareerStage.objects.filter(call=instance).update(enabled=False)

            for career_stage_id in self.cleaned_data['career_stages']:
                CallCareerStage.objects.update_or_create(call=instance, career_stage_id=career_stage_id,
                                                         defaults={'enabled': True})

        return instance

    class Meta:
        model = Call
        fields = ['funding_instrument', 'long_name', 'short_name', 'finance_year', 'description',
                  'introductory_message',
                  'call_open_date', 'submission_deadline', 'budget_maximum',
                  'other_funding_question', 'proposal_partner_question', 'overarching_project_question',
                  'scientific_clusters_question', 'keywords_in_general_information_question',
                  'overall_budget_question']

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
                      'budget_categories': 'If no categories are selected, budget will not appear in the call',
                      'other_funding_question': 'Select if you would like to ask about other funding that will contribute to the proposal',
                      'proposal_partner_question': 'Select if you would like to ask about proposal partners',
                      'overarching_project_question': 'Select if you would to ask about the overarching project',
                      'scientific_clusters_question': 'Select if you would to include a sub-section about "Research Clusters"',
                      'keywords_in_general_information_question': 'Select if you would like to request keywords in the "General Information" section',
                      'overall_budget_question': 'Select if you would like to request the overall budget total. Budget details can be broken down separately by selecting the categories that budget can be allocated to'
                      }

        labels = {
            'scientific_clusters_question': 'Research clusters question',
            'budget_maximum': 'Budget maximum (CHF)',
            'template_questions': ''
        }
