from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelChoiceField, BaseInlineFormSet, BaseFormSet, ModelMultipleChoiceField
from django.forms import ModelForm, Form
from django.forms.models import inlineformset_factory, formset_factory
from crispy_forms.layout import Layout, Div

from ..models import Proposal, ProposalQAText, CallQuestion, Organisation, \
    ProposalFundingItem, ProposedBudgetItem, BudgetCategory, Contact, \
    PhysicalPerson, PersonPosition, PersonTitle

from crispy_forms.helper import FormHelper
from dal import autocomplete


class OrganisationChoiceField(ModelChoiceField):
    def label_from_instance(self, organisation):
        return organisation.abbreviated_name()


class OrganisationMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, organisation):
        return organisation.abbreviated_name()


class PersonForm(Form):
    def __init__(self, *args, **kwargs):
        self.person_position = kwargs.pop('person_position', None)
        super().__init__(*args, **kwargs)

        first_name_initial = surname_initial = organisations_initial = group_initial = \
            academic_title_initial = email_initial = None

        if self.person_position:
            first_name_initial = self.person_position.person.first_name
            surname_initial = self.person_position.person.surname
            organisations_initial = self.person_position.organisations.all()
            group_initial = self.person_position.group
            academic_title_initial = self.person_position.academic_title
            email_initial = self.person_position.contact_set.filter(method=Contact.EMAIL).order_by('date_created')[0].entry

        self.fields['academic_title'] = forms.ModelChoiceField(queryset=PersonTitle.objects.all(),
                                                               help_text='Select from list',
                                                               initial=academic_title_initial)

        self.fields['first_name'] = forms.CharField(initial=first_name_initial,
                                                    label='First name(s)')

        self.fields['surname'] = forms.CharField(initial=surname_initial,
                                                    label='Surname(s)')

        self.fields['email'] = forms.CharField(initial=email_initial,
                                               )

        self.fields['organisations'] = forms.ModelMultipleChoiceField(queryset=Organisation.objects.all(),
                                                                      widget=autocomplete.ModelSelect2Multiple(url='autocomplete-organisations'),
                                                                      initial=organisations_initial,
                                                                      help_text='Please select the organisation(s) to which you are affiliated for the purposes of this proposal',
                                                                      label='Organisation(s)',)

        self.fields['group'] = forms.CharField(initial=group_initial,
                                               help_text='Please type the names of the working group(s) or laboratories to which you are affiliated for the purposes of this proposal',
                                               label='Group / lab')

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('academic_title', css_class='col-2'),
                Div('first_name', css_class='col-5'),
                Div('surname', css_class='col-5'),
                css_class='row'
            ),
            Div(
                Div('email', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('organisations', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('group', css_class='col-12'),
                css_class='row'
            )
        )

    def save_person(self):
        physical_person, created = PhysicalPerson.objects.get_or_create(
            first_name=self.cleaned_data['first_name'],
            surname=self.cleaned_data['surname']
        )

        if self.person_position:
            person_position = self.person_position
        else:
            person_position = PersonPosition()

        person_position.person = physical_person
        person_position.academic_title = self.cleaned_data['academic_title']
        person_position.group = self.cleaned_data['group']

        person_position.save()

        person_position.organisations.set(self.cleaned_data['organisations'])

        try:
            email_contact = person_position.contact_set.get(method=Contact.EMAIL)
        except ObjectDoesNotExist:
            email_contact = Contact()
            email_contact.method = Contact.EMAIL
            email_contact.person_position = person_position

        email_contact.entry = self.cleaned_data['email']
        email_contact.save()

        return person_position


class ProposalForm(ModelForm):
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)

        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['call_id'].initial = self.instance.call.id
        else:
            self.fields['call_id'].initial = self._call.id

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('geographical_areas', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('keywords', css_class='col-12'),
                css_class='r   ow'
            ),
            Div(
                Div('start_timeframe', css_class='col-6'),
                Div('duration', css_class='col-6'),
                css_class='row'
            )
        )

    def save(self, commit=True):
        self.instance.call_id = self.cleaned_data['call_id']

        model = super().save(commit)

        return model

    class Meta:
        model = Proposal
        fields = ['call_id', 'title', 'geographical_areas', 'keywords', 'start_timeframe', 'duration']

        widgets = {'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords')}


class QuestionsForProposalForm(Form):
    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._proposal = kwargs.pop('proposal', None)

        assert self._call or self._proposal

        super().__init__(*args, **kwargs)

        if self._proposal:
            self._call = self._proposal.call

        for question in self._call.callquestion_set.all().order_by('order'):
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

        self.helper = FormHelper(self)
        self.helper.form_tag = False

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['organisation'] = OrganisationChoiceField(queryset=Organisation.objects.all(),
                                                               widget=autocomplete.ModelSelect2(url='autocomplete-organisations'))

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = ProposalFundingItem
        fields = ['organisation', 'funding_status', 'amount', 'proposal', ]
        labels = {'amount': 'Amount (CHF)'}


class ProposalFundingFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'bootstrap4/table_inline_formset.html'
        self.helper.form_id = 'funding_form'

    def save_fundings(self, proposal):
        for form in self.forms:
            if form.cleaned_data:
                if form.cleaned_data['DELETE'] and form.cleaned_data['id']:
                    proposal_item = form.cleaned_data['id']
                    proposal_item.delete()
                elif form.cleaned_data['DELETE'] is False:
                    proposal_item = form.save(commit=False)
                    proposal_item.proposal = proposal
                    proposal_item.save()


# See documentation in: https://medium.com/@adandan01/django-inline-formsets-example-mybook-420cc4b6225d
ProposalFundingItemFormSet = inlineformset_factory(
    Proposal, ProposalFundingItem, form=ProposalFundingItemForm, formset=ProposalFundingFormSet, extra=1,
    can_delete=True)


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
    amount = forms.DecimalField(required=False, label='Amount (CHF)')

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
                initial_budget.append({'id': proposed_item_budget.id, 'category': proposed_item_budget.category,
                                       'amount': proposed_item_budget.amount, 'details': proposed_item_budget.details})

            kwargs['initial'] = initial_budget

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False


    def clean(self):
        super().clean()

        budget_amount = 0
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
                'Maximum budget for this call is {} total budget for your proposal {}'.format(maximum_budget,
                                                                                              budget_amount))

    def save_budgets(self, proposal):
        for form in self.forms:
            form.save_budget(proposal)


BudgetItemFormSet = formset_factory(BudgetItemForm, formset=BudgetFormSet, can_delete=False, extra=0)
