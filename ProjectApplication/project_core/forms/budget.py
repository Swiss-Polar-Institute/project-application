import decimal

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.humanize.templatetags.humanize import number_format
from django.forms import BaseFormSet, formset_factory

from project_core.forms.utils import PlainTextWidget
from project_core.models import BudgetCategory, ProposedBudgetItem


class BudgetItemForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    category = forms.CharField(widget=PlainTextWidget())
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}))
    amount = forms.DecimalField(required=False, label='Total (CHF)', localize=True,
                                widget=forms.TextInput(attrs={'size': '5'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_valid()

        if 'initial' in kwargs:
            category = kwargs['initial']['category']
        else:
            category_id = self.cleaned_data['category']
            category = BudgetCategory.objects.get(id=category_id)

        self.fields['category'].help_text = category.name
        self.fields['category'].value = category.id

        self.fields['amount'].widget.attrs['min'] = 0

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    def save_budget(self, proposal):
        if self.cleaned_data['id']:
            budget_item = ProposedBudgetItem.objects.get(id=self.cleaned_data['id'])
        else:
            budget_item = ProposedBudgetItem()

        budget_item.amount = self.cleaned_data['amount']
        budget_item.details = self.cleaned_data['details']
        budget_item.category = BudgetCategory.objects.get(id=self.cleaned_data['category'])
        budget_item.proposal = proposal

        budget_item.save()

    def clean(self):
        cleaned_data = super().clean()

        category = BudgetCategory.objects.get(id=cleaned_data['category'])

        if 'amount' not in cleaned_data:
            self.add_error('amount', 'Please write a number (do not use thousands separator if you have a problem)')
            amount = 0
        else:
            amount = cleaned_data['amount'] or 0

        details = cleaned_data['details'] or ''

        if details == '':
            if amount > 0:
                self.add_error('details', 'Please fill in details {}'.format(category))
        else:
            if amount == 0:
                self.add_error('details', 'Please declare a budget amount {}'.format(category))

        if amount < 0:
            self.add_error('amount', 'Cannot be negative {}'.format(category))

        return cleaned_data


class BudgetFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        proposal = kwargs.pop('proposal', None)
        self._call = kwargs.pop('call', None)

        if proposal:
            initial_budget = []

            for proposed_item_budget in ProposedBudgetItem.objects.filter(proposal=proposal).order_by('category__order',
                                                                                                      'category__name'):
                initial_budget.append({'id': proposed_item_budget.id, 'category': proposed_item_budget.category,
                                       'amount': proposed_item_budget.amount, 'details': proposed_item_budget.details})

            kwargs['initial'] = initial_budget

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    def clean(self):
        super().clean()

        budget_amount = decimal.Decimal('0.00')
        maximum_budget = self._call.budget_maximum

        if not self.is_valid():
            # if one of the budget items is not valid: doesn't validate the general form
            # E.g. if an amount is negative it will have an error in the amount but the
            # amount is removed from the form.cleaned_data
            return

        for budget_item_form in self.forms:
            amount = budget_item_form.cleaned_data['amount'] or 0

            budget_amount += amount

        if budget_amount > maximum_budget:
            raise forms.ValidationError(
                'Maximum allowed budget for this call is {} CHF. Your total proposed budget is {} CHF'.format(
                    number_format(maximum_budget),
                    number_format(budget_amount)))

    def save_budgets(self, proposal):
        for form in self.forms:
            form.save_budget(proposal)


BudgetItemFormSet = formset_factory(BudgetItemForm, formset=BudgetFormSet, can_delete=False, extra=0)

# It's used like:
# budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)
