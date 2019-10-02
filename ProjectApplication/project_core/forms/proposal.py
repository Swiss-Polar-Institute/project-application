from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelChoiceField, BaseInlineFormSet, BaseFormSet
from django.forms import ModelForm, Form
from django.forms.models import inlineformset_factory, formset_factory


from ..models import Person, Proposal, ProposalQAText, CallQuestion, Keyword, Organisation, \
    ProposalFundingItem, ProposedBudgetItem, BudgetCategory


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisations', 'group', ]


class OrganisationChoiceField(ModelChoiceField):
    def label_from_instance(self, organisation):
        return organisation.abbreviated_name()


class ProposalForm(ModelForm):
    keywords_str = forms.CharField(label='Keywords', help_text='Separated by commas', )
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
        else:
            self.fields['call_id'].initial = self._call.id

        keywords_list = []
        if self.instance.id:
            for keyword in self.instance.keywords.all().order_by('name'):
                keywords_list.append(keyword.name)

            self.fields['keywords_str'] = forms.CharField(label='Keywords',
                                                          help_text='Separated by commas',
                                                          initial=', '.join(keywords_list))

    def save(self, commit=True):
        self.instance.call_id = self.cleaned_data['call_id']
        # TODO: verify permissions/that the call is open/etc.

        model = super().save(commit)

        if commit:
            model.keywords.clear()

            for keyword_str in self.cleaned_data['keywords_str'].split(','):
                keyword_str = keyword_str.strip(' ')
                keyword = Keyword.objects.get_or_create(name=keyword_str)[0]
                model.keywords.add(keyword)

            model.geographical_areas.set(self.cleaned_data['geographical_areas'])

        return model

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'start_timeframe', 'duration']


class QuestionsForProposalForm(Form):
    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._proposal = kwargs.pop('proposal', None)

        assert self._call or self._proposal

        super().__init__(*args, **kwargs)

        if self._proposal:
            self._call = self._proposal.call

        for question in self._call.callquestion_set.all().order_by('question_text'):
            answer = None
            if self._proposal:
                try:
                    answer = ProposalQAText.objects.get(proposal=self._proposal, call_question=question).answer
                except ObjectDoesNotExist:
                    pass

            question_text = question.question_text
            if question.answer_max_length:
                question_text += ' (maximum {} words)'.format(question.answer_max_length)

            self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question_text,
                                                                             widget=forms.Textarea(),
                                                                             initial=answer,
                                                                             help_text=question.question_description)

    def save_answers(self, proposal):
        for question, answer in self.cleaned_data.items():
            call_question_id = int(question[len('question_'):])

            ProposalQAText.objects.update_or_create(
                proposal=proposal, call_question_id=call_question_id,
                defaults={'answer': answer}
            )

    def clean(self):
        cleaned_data = super().clean()

        # list because otherwise dictionary size changes during execution
        # (need to check why exactly)
        for question_number in list(cleaned_data.keys()):
            answer = cleaned_data[question_number]
            question_id = question_number[len('question_'):]

            call_question = CallQuestion.objects.get(id=question_id)

            max_word_length = call_question.answer_max_length
            current_words = len(answer.split())

            if current_words > max_word_length:
                self.add_error(question_number,
                               'Too long. Current: {} words, maximum: {} words'.format(current_words, max_word_length))

        return cleaned_data


class ProposalFundingItemForm(ModelForm):
    organisation = OrganisationChoiceField(queryset=Organisation.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProposalFundingItem
        fields = ['organisation', 'status', 'amount', 'proposal', ]


class ProposalFundingFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_fundings(self, proposal):
        for form in self.forms:
            if form.cleaned_data:
                proposal_item = form.save(commit=False)
                proposal_item.proposal = proposal
                proposal_item.save()

# See documentation in: https://medium.com/@adandan01/django-inline-formsets-example-mybook-420cc4b6225d
ProposalFundingItemFormSet = inlineformset_factory(
    Proposal, ProposalFundingItem, form=ProposalFundingItemForm, formset=ProposalFundingFormSet, extra=1, can_delete=True)


class PlainTextWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            if type(value) == str:
                final_value = value
            else:
                final_value = value.id

            return '<input type="hidden" name="{}" value="{}" id="{}">'.format(name, final_value, attrs['id'])
        else:
            return '-'


class BudgetItemForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    category = forms.CharField(widget=PlainTextWidget())
    details = forms.CharField(required=False)
    amount = forms.DecimalField(required=False)

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

        budget_amount = 0

        amount = cleaned_data['amount'] or 0
        details = cleaned_data['details'] or ''
        category = BudgetCategory.objects.get(id=cleaned_data['category'])

        budget_amount += amount

        if amount > 0 and details == '':
            self.add_error('details', 'Please fill in details'.format(category))

        if amount < 0:
            self.add_error('amount', 'Cannot be negative'.format(category))

        return cleaned_data


class BudgetFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        proposal = kwargs.pop('proposal', None)
        self._call = kwargs.pop('call', None)

        if proposal:
            initial_budget = []

            for proposed_item_budget in ProposedBudgetItem.objects.filter(proposal=proposal):
                initial_budget.append({'id': proposed_item_budget.id, 'category': proposed_item_budget.category, 'amount': proposed_item_budget.amount, 'details': proposed_item_budget.details})

            kwargs['initial'] = initial_budget

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        budget_amount = 0
        maximum_budget = self._call.budget_maximum

        for budget_item_form in self.forms:
            amount = budget_item_form.cleaned_data['amount'] or 0

            budget_amount += amount

        if budget_amount > maximum_budget:
            raise forms.ValidationError('Maximum budget for this call is {} total budget for your proposal {}'.format(maximum_budget, budget_amount))

    def save_budgets(self, proposal):
        for form in self.forms:
            form.save_budget(proposal)


BudgetItemFormSet = formset_factory(BudgetItemForm, formset=BudgetFormSet, can_delete=False, extra=0)
