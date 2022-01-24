from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.urls import reverse
from django.utils.html import format_html

from ProjectApplication import settings
from evaluation.models import CallEvaluation, Reviewer, CriterionCallEvaluation, Criterion
from evaluation.utils import ReviewerMultipleChoiceField
from project_core.forms.utils import cancel_edit_button
from project_core.utils.utils import user_is_in_group_name
from project_core.widgets import XDSoftYearMonthDayPickerInput, CheckboxSelectMultipleSortable


def add_missing_criterion_call_evaluation(call_evaluation):
    # TODO: refactor with add_missing_budget_categories
    all_criterion_ids = Criterion.objects.all().values_list('id', flat=True)
    criterion_call_evaluation_ids = CriterionCallEvaluation.objects.filter(call_evaluation=call_evaluation).values_list(
        'criterion__id',
        flat=True)

    missing_ids = set(all_criterion_ids) - set(criterion_call_evaluation_ids)

    # New items are listed at the bottom. The order only appears if the user changes the order.
    # current_maximum is used to ensure that the new ones are added at the bottom: same as they are displayed
    current_maximum = CriterionCallEvaluation.objects. \
        filter(call_evaluation=call_evaluation). \
        aggregate(Max('order'))['order__max']

    if current_maximum is None:
        current_maximum = 1

    for missing_id in missing_ids:
        try:
            criterion = Criterion.objects.get(id=missing_id)
        except ObjectDoesNotExist:
            # This criterion has been deleted between the time that the form was presented to now
            continue

        CriterionCallEvaluation.objects.create(call_evaluation=call_evaluation, criterion_id=missing_id, enabled=False,
                                               order=current_maximum)
        current_maximum += 1


class CallEvaluationForm(forms.ModelForm):
    FORM_NAME = 'call_evaluation_form'

    def __init__(self, *args, **kwargs):
        call = kwargs.pop('call', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        if self.instance.id:
            self.helper.form_action = reverse('logged-call-evaluation-update', kwargs={'pk': self.instance.id})
            self.fields['call'].initial = call = self.instance.call
        else:
            self.helper.form_action = reverse('logged-call-evaluation-add') + f'?call={call.id}'
            self.fields['call'].initial = call

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['panel_date'])

        if hasattr(call, 'callevaluation'):
            cancel_edit_url = reverse('logged-call-evaluation-detail', kwargs={'pk': call.callevaluation.id})
            initial_reviewers = call.reviewer_set.all()
        else:
            cancel_edit_url = reverse('logged-call-evaluation-add') + f'?call={call.id}'
            initial_reviewers = []

        reviewer_add_url = reverse('logged-user-add')

        reviewers_help_text = \
            f'Select the reviewers that you would like to be added for this call. This is everyone that ' \
            f'will review individual proposals and be on the review panel. If you cannot find the person ' \
            f'you are looking for, please <a href="{reviewer_add_url}">add a Reviewer type of user</a> and reload ' \
            f'this page.'

        self.fields['reviewers'] = ReviewerMultipleChoiceField(initial=initial_reviewers,
                                                               queryset=Reviewer.objects.all(),
                                                               required=True,
                                                               widget=FilteredSelectMultiple(
                                                                   is_stacked=True,
                                                                   verbose_name='reviewers'),
                                                               help_text=reviewers_help_text)

        criterion_choices, criterion_initial = CheckboxSelectMultipleSortable.get_choices_initial(
            CriterionCallEvaluation,
            self.instance, 'call_evaluation',
            Criterion, 'criterion',
            label_from_instance=lambda obj: format_html('{} <small>({})</small>', obj.name, obj.description)
        )

        evaluation_criteria_list_url = reverse('logged-evaluation_criteria-list')
        list_edit_criteria = f'You can list and create criteria in <a href="{evaluation_criteria_list_url}">Evaluation criteria list</a>.'

        self.fields['criteria'] = forms.MultipleChoiceField(choices=criterion_choices,
                                                            initial=criterion_initial,
                                                            widget=CheckboxSelectMultipleSortable,
                                                            label='Criteria (drag and drop to order them)',
                                                            help_text=f'These criteria are used in the Excel Evaluation sheet. '
                                                                      f'{list_edit_criteria}'
                                                            )

        self.criteria_order_key = f'criteria-{CheckboxSelectMultipleSortable.order_of_values_name}'

        self.helper.layout = Layout(
            Div(
                Div('call', css_class='col-12', hidden=True),
                css_class='row'
            ),
            Div(
                Div('reviewers', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('panel_date', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('criteria', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('post_panel_management_table', css_class='col-12'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Call Evaluation'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        data_evaluation_criteria_order_key = f'{self.prefix}-{self.criteria_order_key}'

        self.cleaned_data[self.criteria_order_key] = CheckboxSelectMultipleSortable.get_clean_order(self.data,
                                                                                                    data_evaluation_criteria_order_key)

        return cleaned_data

    def save_call_evaluation(self, user, *args, **kwargs):
        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionError()

        reviewers = self.cleaned_data['reviewers']

        call_evaluation = super().save(*args, **kwargs)

        CheckboxSelectMultipleSortable.save(CriterionCallEvaluation, call_evaluation,
                                            'call_evaluation', Criterion, 'criterion',
                                            self.cleaned_data['criteria'],
                                            self.cleaned_data[self.criteria_order_key]
                                            )

        call_evaluation.call.reviewer_set.set(reviewers)

        return call_evaluation

    class Meta:
        model = CallEvaluation

        fields = ['call', 'panel_date', 'post_panel_management_table']

        widgets = {
            'panel_date': XDSoftYearMonthDayPickerInput
        }
