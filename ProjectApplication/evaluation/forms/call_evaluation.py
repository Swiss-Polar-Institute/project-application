import logging
import re

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Max
from django.urls import reverse

from ProjectApplication import settings
from evaluation.models import CallEvaluation, Reviewer, CriterionCallEvaluation, Criterion
from evaluation.utils import ReviewerMultipleChoiceField
from project_core.forms.utils import cancel_edit_button
from project_core.utils.utils import user_is_in_group_name
from project_core.widgets import XDSoftYearMonthDayPickerInput, CheckboxSelectMultipleSortable

logger = logging.getLogger('evaluation')


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

        self.fields['reviewers'] = ReviewerMultipleChoiceField(initial=initial_reviewers,
                                                               queryset=Reviewer.objects.all(),
                                                               required=True,
                                                               widget=FilteredSelectMultiple(
                                                                   is_stacked=True,
                                                                   verbose_name='reviewers'),
                                                               help_text=self.Meta.help_texts['reviewers'])

        criterion_choices, criterion_initial = CheckboxSelectMultipleSortable.get_choices_initial(
            CriterionCallEvaluation,
            CallEvaluation, self.instance, 'call_evaluation',
            Criterion, 'criterion')

        self.fields['criteria'] = forms.MultipleChoiceField(choices=criterion_choices,
                                                            initial=criterion_initial,
                                                            widget=CheckboxSelectMultipleSortable,
                                                            label='Criteria (drag and drop to sort them)',
                                                            help_text='These criteria are used in the Excel Evaluation sheet'
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
                Div('criteria', css_class='col-6'),
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

        if data_evaluation_criteria_order_key in self.data:
            order_data = self.data[data_evaluation_criteria_order_key]

            if order_data == '':
                self.cleaned_data[self.criteria_order_key] = None
            elif re.search(r'^(\d+,)*\d+$', order_data):
                # The order for the list is like '4,3,1,10' (starts with a number, has commas, ends with a number)
                self.cleaned_data[self.criteria_order_key] = order_data
            else:
                logger.warning(
                    f'NOTIFY: Error when parsing order of the criterion categories. Received: {order_data}')

                raise ValidationError(
                    'Error when parsing order of the criterion categories. Try again or contact Project Application administrators')
        else:
            self.cleaned_data[self.criteria_order_key] = None

        return cleaned_data

    def save_call_evaluation(self, user, *args, **kwargs):
        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionError()

        reviewers = self.cleaned_data['reviewers']

        call_evaluation = super().save(*args, **kwargs)

        CheckboxSelectMultipleSortable.add_missing_related_objects(CriterionCallEvaluation, call_evaluation,
                                                                   'call_evaluation', Criterion,
                                                                   'criterion')
        CheckboxSelectMultipleSortable.save_enabled_disabled(CriterionCallEvaluation, CallEvaluation,
                                                             call_evaluation, 'call_evaluation',
                                                             'criterion',
                                                             self.cleaned_data['criteria'])
        CheckboxSelectMultipleSortable.save_order(CriterionCallEvaluation, call_evaluation,
                                                  'call_evaluation', 'criterion',
                                                  self.cleaned_data.get(self.criteria_order_key, None))

        call_evaluation.call.reviewer_set.set(reviewers)

        return call_evaluation

    class Meta:
        model = CallEvaluation

        fields = ['call', 'panel_date', 'post_panel_management_table']

        help_texts = {
            'reviewers': 'Select the reviewers that you would like to be added for this call. This is everyone that '
                         'will review individual proposals and be on the review panel. If you cannot find the person '
                         'you are looking for, please contact Carles to add them. This is not currently possible as a '
                         'management user.'
        }

        widgets = {
            'panel_date': XDSoftYearMonthDayPickerInput
        }
