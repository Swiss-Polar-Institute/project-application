from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelChoiceField, BaseModelFormSet, BaseInlineFormSet, BaseFormSet
from django.forms import ModelForm, Form
from django.forms.models import inlineformset_factory, formset_factory, modelformset_factory
from django.utils.safestring import mark_safe
from django.db.models import F


from ..models import Person, Proposal, ProposalQAText, CallQuestion, Keyword, Organisation, FundingStatus, \
    ProposalFundingItem, ProposedBudgetItem, BudgetItem, BudgetCategory


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisations', 'group', ]


class OrganisationChoiceField(ModelChoiceField):
    def label_from_instance(self, organisation):
        return organisation.abbreviated_name()


class ProposalFundingItemForm(ModelForm):
    organisation = OrganisationChoiceField(queryset=Organisation.objects.all())

    def __init__(self, *args, **kwargs):
        super(ProposalFundingItemForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ProposalFundingItem
        fields = ['organisation', 'status', 'amount', 'proposal', ]


class ProposalForm(ModelForm):
    keywords_str = forms.CharField(label='Keywords', help_text='Separated by commas', )
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super(ProposalForm, self).__init__(*args, **kwargs)

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

        model = super(ProposalForm, self).save(commit)

        if commit:
            model.keywords.clear()

            for keyword_str in self.cleaned_data['keywords_str'].split(','):
                keyword_str = keyword_str.strip(' ')
                keyword = Keyword.objects.get_or_create(name=keyword_str)[0]
                model.keywords.add(keyword)

        return model

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'start_timeframe', 'duration']


class QuestionsForProposalForm(Form):
    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._proposal = kwargs.pop('proposal', None)

        assert self._call or self._proposal

        super(QuestionsForProposalForm, self).__init__(*args, **kwargs)

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

    def save_answers(self):
        # for question in self._call.callquestion_set.all():
        #     answer = self.cleaned_data['']
        for question, answer in self.cleaned_data.items():
            call_question_id = int(question[len('question_'):])

            ProposalQAText.objects.update_or_create(
                proposal_id=self._proposal_id, call_question_id=call_question_id,
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


# class BudgetForm(Form):
#     def __init__(self, *args, **kwargs):
#         self._call: Call = kwargs.pop('call', None)
#         self._proposal: Proposal = kwargs.pop('proposal', None)
#
#         assert self._call or self._proposal
#
#         if self._proposal:
#             self._call = self._proposal.call
#
#         super(BudgetForm, self).__init__(*args, **kwargs)
#
#         for budget_category in self._call.budget_categories.all().order_by('name'):
#             self.fields['category_budget_name_%d' % budget_category.id] = forms.CharField(
#                 help_text=budget_category.description, widget=forms.HiddenInput(), required=False)
#
#             proposal_details = None
#             proposal_amount = None
#
#             if self._proposal:
#                 proposed_budget_item = ProposedBudgetItem.objects.get(proposal=self._proposal, category=budget_category)
#                 proposal_details = proposed_budget_item.details
#                 proposal_amount = proposed_budget_item.amount
#
#             self.fields['details_%d' % budget_category.id] = forms.CharField(initial=proposal_details, required=False)
#             self.fields['amount_%d' % budget_category.id] = forms.DecimalField(initial=proposal_amount)
#
#     def clean(self):
#         cleaned_data = super(BudgetForm, self).clean()
#
#         budget_amount = 0
#
#         maximum_budget = self._call.budget_maximum
#
#         for budget_category in self._call.budget_categories.all():
#             amount = cleaned_data['amount_%d' % budget_category.id]
#             detail = cleaned_data['details_%d' % budget_category.id]
#             budget_description = budget_category.description
#             field_for_validation = 'category_budget_name_%d' % budget_category.id
#
#             budget_amount += amount
#
#             if amount > maximum_budget:
#                 self.add_error(field_for_validation, 'Amount of item "{}" exceeds the total maximum budget'.format(budget_description))
#
#             if amount > 0 and detail == '':
#                 self.add_error(field_for_validation, 'Details of item "{}" cannot be empty because the value is not 0'.format(budget_description))
#
#             if amount < 0:
#                 self.add_error(field_for_validation, 'Amount of item "{}" is negative. Amount cannot be negative'.format(budget_description))
#
#         if budget_amount > maximum_budget:
#             self.add_error(None,
#                            'Maximum budget for this call is {} total budget for your proposal {}'.format(maximum_budget, budget_amount))
#
#         return cleaned_data
#
#     def save_budget(self):
#         for budget_category in self._call.budget_categories.all():
#
#             ProposedBudgetItem.objects.update_or_create(
#                 proposal=Proposal.objects.get(id=self._proposal_id),
#                 category=budget_category,
#                 defaults={
#                     'details': self.cleaned_data['details_%d' % budget_category.id],
#                     'amount': self.cleaned_data['amount_%d' % budget_category.id]
#                 }
#             )
#

class FundingOrganisationsForm(Form):
    def __init__(self, *args, **kwargs):
        super(FundingOrganisationsForm, self).__init__(*args, **kwargs)

        organisations = FundingOrganisationsForm._organisations_tuple()
        for funding_status in FundingStatus.objects.all().order_by('status'):
            self.fields['funding_status_name_%d' % funding_status.id] = forms.CharField(
                help_text=funding_status.status, widget=forms.HiddenInput(), required=True)

            self.fields['source_of_funding_%d' % funding_status.id] = forms.ChoiceField(
                choices=organisations, required=True)

            self.fields['amount_%d' % funding_status.id] = forms.DecimalField(required=True)

    def clean(self):
        cleaned_data = super(FundingOrganisationsForm, self).clean()
        return cleaned_data

    @staticmethod
    def _organisations_tuple():
        organisations = []

        for organisation in Organisation.objects.all().order_by('short_name'):
            organisations.append((organisation.id, organisation.abbreviated_name()), )

        organisations.append((99, 'Other'), )
        return organisations


# See documentation in: https://medium.com/@adandan01/django-inline-formsets-example-mybook-420cc4b6225d
ProposalFundingItemFormSet = inlineformset_factory(
    Proposal, ProposalFundingItem, form=ProposalFundingItemForm, extra=1, can_delete=True)


# class ProposalBudgetItemCategoryAsText(Select):
#     def render(self, name, value, attrs=None, renderer=None):
#         category = BudgetCategory.objects.get(id=value).name
#         ret = SafeText('{}<input type="hidden" name="{}" value="{} id="{}">'.format(category, name, value, attrs['id']))
#         return ret

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



# class BudgetItemForm(ModelForm):
#     category = forms.CharField(widget=PlainTextWidget())
#     details = forms.CharField()
#     id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(BudgetItemForm, self).__init__(*args, **kwargs)
#         self.fields['category'] = forms.CharField(widget=PlainTextWidget())
#         self.order_fields(['category', 'details', 'amount', 'id'])
#
#
#         print('cleaned_data', hasattr(self, 'cleaned_data'))
#
#         print('hasattr before:', hasattr(self, 'cleaned_data'))
#         print('is_valid:', self.is_valid())
#         print('hasattr after:', hasattr(self, 'cleaned_data'))
#
#         if 'initial' in kwargs:
#             category = kwargs['initial']['category']
#         elif hasattr(self, 'cleaned_data'):
#             category_id = self.cleaned_data['category']
#             category = BudgetCategory.objects.get(id=category_id)
#         else:
#             category = None
#
#         print('cleaned_data', hasattr(self, 'cleaned_data'))
#
#         self.fields['category'].help_text = category.name
#
#         print('test')
#
#         # self.is_valid()
#         # self.fields['category'].help_text = self.cleaned_data['category'].name
#         # print(self.fields['category'].help_text)
#         # self.fields['test'] = forms.CharField()
#         # self.fields['test'].help_test = 'hi'
#         # self._category_id = None
#
#         # needed to ensure that self.cleaned_data exists
#         # self.is_valid()
#
#         # print('00 hasattr self cleaned_data', hasattr(self, 'cleaned_data'))
#         #
#         # if self.instance and self.instance.category:
#         #     self._category_id = self.instance.category.id
#         # elif 'category' in self.initial:
#         #     self._category_id = self.initial['category'].id
#         # elif hasattr(self, 'cleaned_data'):
#         #     self._category_id = self.cleaned_data['category'].id
#         # else:
#         #     self._category_id = None
#         #
#         # # print('self_cleaned_data:', self.cleaned_data)
#         # print('00 hasattr self cleaned_data', hasattr(self, 'cleaned_data'))
#         #
#         # if self._category_id:
#         #     self.fields['category'].help_text = BudgetCategory.objects.get(id=self._category_id).name
#         #     self.fields['category'].initial = BudgetCategory.objects.get(id=self._category_id)
#         #     self.fields['category'].long_help = 'test'
#         #
#         # else:
#         #     print('no category_id')
#         #
#         # print('init category_id', self._category_id)
#
#         # category_help_text = '{}: {}'.format(initial.get('name'), initial.get('description'))
#         #
#         # self.fields['category'] = forms.CharField(label='Category', widget=forms.HiddenInput(), required=False,
#         #                                           help_text=category_help_text)
#         #
#         # self.fields['details'] = forms.CharField(label='Details', initial=initial.get('details', None))
#         # self.fields['amount'] = forms.DecimalField(label='Amount', initial=initial.get('amount', None))
#
#         # category_help_text = '{}: {}'.format(initial.get('name'), initial.get('description'))
#         # self.fields['category'] = forms.CharField(label='Category', widget=forms.HiddenInput(), required=False,
#         #                                           help_text=category_help_text)
#
#     def clean(self):
#         cleaned_data = super(BudgetItemForm, self).clean()
#
#         # print('clean category:', cleaned_data['category'])
#         # cleaned_data['category'] = BudgetCategory.objects.get(id=cleaned_data['category'])
#         # cleaned_data['category'] = BudgetCategory.objects.get(id=cleaned_data['category'])
#         # cleaned_data['category'] = int(cleaned_data['category'])
#         # cleaned_data['category'] = BudgetCategory.objects.get(id=cleaned_data['category_id'])
#
#         return cleaned_data
#
#     class Meta:
#         model = ProposedBudgetItem
#         fields = ['id', 'details', 'amount', ]
#
#
#
#
# class BaseBudgetItemFormSet(BaseInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         if 'call' in kwargs:
#             self._call = kwargs.pop('call')
#         elif self.instance:
#             self._call = self.instance.call
#         else:
#             assert False
#
#         super(BaseBudgetItemFormSet, self).__init__(*args, **kwargs)
#
#         # if form_kwargs:
#         #     # if 'call' in form_kwargs:
#         #     #     call = form_kwargs['call']
#         #     #
#         #     #     self.queryset = call.budget_categories.annotate(category=F('name'))
#         #     #
#         #     if 'proposal' in form_kwargs:
#         #         proposal = form_kwargs['proposal']
#         #         self.queryset = ProposedBudgetItem.objects.filter(proposal=proposal)
#
#     # def is_valid(self):
#     #     return super(BaseBudgetItemFormSet, self).is_valid()
#
#     def clean(self):
#         super(BaseBudgetItemFormSet, self).clean()
#
#         budget_amount = 0
#         maximum_budget = self._call.budget_maximum
#
#         for budget_item_form in self.forms:
#             amount = budget_item_form.cleaned_data.get('amount', 0)
#
#             budget_amount += amount
#
#         if budget_amount > maximum_budget:
#             raise forms.ValidationError('Maximum budget for this call is {} total budget for your proposal {}'.format(maximum_budget, budget_amount))
#
#
# BudgetItemFormSet = inlineformset_factory(Proposal, ProposedBudgetItem, form=BudgetItemForm, formset=BaseBudgetItemFormSet, can_delete=False, extra=0)
#
#
# def budget_form_factory(extra):
#     return inlineformset_factory(Proposal, ProposedBudgetItem, form=BudgetItemForm, formset=BaseBudgetItemFormSet, can_delete=False, extra=extra)


class BudgetItemForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    category = forms.CharField(widget=PlainTextWidget())
    details = forms.CharField()
    amount = forms.DecimalField()

    def __init__(self, *args, **kwargs):
        super(BudgetItemForm, self).__init__(*args, **kwargs)

        self.is_valid()

        if 'initial' in kwargs:
            category = kwargs['initial']['category']
        else:
            category_id = self.cleaned_data['category']
            category = BudgetCategory.objects.get(id=category_id)

        self.fields['category'].help_text = category.name
        self.fields['category'].value = category.id

    def save_budget(self):
        budget_item = BudgetItem()
        budget_item.amount = self.cleaned_data['amount']
        budget_item.details = self.cleaned_data['details']
        budget_item.category = BudgetCategory.objects.get(id=self.cleaned_data['category'])


class BudgetFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        call = kwargs.pop('call', None)
        instance = kwargs.pop('instance', None)

        super(BudgetFormSet, self).__init__(*args, **kwargs)


BudgetItemFormSet = formset_factory(BudgetItemForm, formset=BudgetFormSet, can_delete=False, extra=0)


def budget_form_factory(extra):
    return formset_factory(BudgetItemForm, formset=BudgetFormSet, can_delete=False, extra=extra)
