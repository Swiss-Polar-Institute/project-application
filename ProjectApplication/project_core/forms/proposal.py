from django import forms
from django.forms import ModelForm, Form
from ..models import Person, Proposal, Call, ProposalQAText, CallQuestion, BudgetCategory, Keyword, ProposedBudgetItem
from django.core.exceptions import ObjectDoesNotExist


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisations', 'group', ]


class ProposalForm(ModelForm):
    keywords_str = forms.CharField(label='Keywords', help_text='Separated by commas', )
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call_id = kwargs.pop('call_id', None)
        self._proposal_id = kwargs.pop('proposal_id', None)

        super(ProposalForm, self).__init__(*args, **kwargs)

        self.fields['call_id'].initial = self._call_id

        keywords_list = []
        if self._proposal_id is not None:
            for keyword in Proposal.objects.get(id=self._proposal_id).keywords.all():
                keywords_list.append(keyword.name)

            self.fields['keywords_str'] = forms.CharField(label='Keywords',
                                                          help_text='Separated by commas',
                                                          initial=', '.join(keywords_list))

    def save(self, commit=True):
        self.instance.call_id = self.cleaned_data['call_id']

        model = super(ProposalForm, self).save(commit)

        if commit:
            for keyword_str in self.cleaned_data['keywords_str'].split(','):
                keyword_str = keyword_str.strip(' ')
                keyword = Keyword.objects.get_or_create(name=keyword_str)[0]
                model.keywords.add(keyword)

        return model

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'start_timeframe', 'duration']


class QuestionsForProposal(Form):
    def __init__(self, *args, **kwargs):
        self.call_id = kwargs.pop('call_id', None)
        self.proposal_id = kwargs.pop('proposal_id', None)

        assert (self.call_id is not None) or (self.proposal_id is not None)

        super(QuestionsForProposal, self).__init__(*args, **kwargs)

        if self.call_id is not None:
            # This is a form with questions but not answers yet
            for question in Call.objects.get(id=self.call_id).callquestion_set.all():
                self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text,
                                                                                 widget=forms.Textarea())

        if self.proposal_id is not None:
            # This is a form with already answers
            for question in Proposal.objects.get(id=self.proposal_id).call.callquestion_set.all():
                try:
                    answer = ProposalQAText.objects.get(proposal=self.proposal_id, call_question=question.id).answer
                except ObjectDoesNotExist:
                    answer = None

                self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text,
                                                                                 widget=forms.Textarea(),
                                                                                 initial=answer)

    def save_answers(self):
        for question, answer in self.cleaned_data.items():
            call_question_id = int(question[len('question_'):])

            qa_text = ProposalQAText(proposal_id=self.proposal_id, call_question_id=call_question_id, answer=answer)
            qa_text.save()

    def clean(self):
        cleaned_data = super(QuestionsForProposal, self).clean()

        # list because otherwise dictionary size changes during execution
        # (need to check why exactly)
        for question_number in list(cleaned_data.keys()):
            answer = cleaned_data[question_number]
            question_id = question_number[len('question_'):]

            call_question = CallQuestion.objects.get(id=question_id)

            max_word_length = call_question.answer_max_length
            current_words = len(answer.split())

            if current_words > max_word_length:
                self.add_error(question_number, 'Too long. Current: {} words, maximum: {}'.format(current_words, max_word_length))

        return cleaned_data


class BudgetForm(Form):
    def __init__(self, *args, **kwargs):
        self.call_id = kwargs.pop('call_id', None)
        self.proposal_id = kwargs.pop('proposal_id', None)

        assert (self.call_id is not None) or (self.proposal_id is not None)

        super(BudgetForm, self).__init__(*args, **kwargs)

        if self.call_id is not None:
            for budget_category in Call.objects.get(id=self.call_id).budget_categories.all():
                self.fields['category_budget_name_%d' % budget_category.id] = forms.CharField(
                    help_text=budget_category.description, widget=forms.HiddenInput(), required=False)
                self.fields['details_%d' % budget_category.id] = forms.CharField()
                self.fields['amount_%d' % budget_category.id] = forms.DecimalField()

        if self.proposal_id is not None:
            for proposed_budget_item in ProposedBudgetItem.objects.filter(proposal_id=self.proposal_id):
                budget_category_id = proposed_budget_item.category.id
                self.fields['category_budget_name_%d' % budget_category_id] = forms.CharField(
                    help_text=proposed_budget_item.category.name, widget=forms.HiddenInput(), required=False)
                self.fields['details_%d' % budget_category_id] = forms.CharField(initial=proposed_budget_item.details)
                self.fields['amount_%d' % budget_category_id] = forms.DecimalField(initial=proposed_budget_item.amount)


    def clean(self):
        cleaned_data = super(BudgetForm, self).clean()

        maximum_budget = 1000
        budget_amount = 0

        for key in list(cleaned_data.keys()):
            answer = cleaned_data[key]

            if key.startswith('amount_'):
                budget_amount += answer

            if key.startswith('amount_') and answer > maximum_budget:
                number = int(key[len('amount_'):])
                budget_name = self.fields['category_budget_name_%d' % number]
                self.add_error(key, 'Amount of item "{}" exceeds the maximum budget'.format(budget_name.help_text))

        if budget_amount > maximum_budget:
            self.add_error(None,
                           'Maximum budget for this call is {} total budget for your proposal {}'.format(maximum_budget, budget_amount))

        return cleaned_data

    def save_budget(self):
        for budget_category in Call.objects.get(id=self.call_id).budget_categories.all():
            proposed_budget_item = ProposedBudgetItem()
            proposed_budget_item.category = budget_category
            proposed_budget_item.details = self.cleaned_data['details_%d' % budget_category.id]
            proposed_budget_item.amount = self.cleaned_data['amount_%d' % budget_category.id]
            proposed_budget_item.proposal = Proposal.objects.get(id=self.proposal_id)

            proposed_budget_item.save()
