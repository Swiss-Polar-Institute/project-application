from dal import autocomplete
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from ..forms.proposal import PersonForm, ProposalForm, QuestionsForProposalForm, ProposalFundingItemFormSet, \
    BudgetItemFormSet, DataCollectionForm
from ..models import Proposal, Call, ProposalStatus, Organisation, Keyword, Source, KeywordUid, ProposalQAText

# Form names (need to match what's in the templates)
PROPOSAL_FORM_NAME = 'proposal_form'
PERSON_FORM_NAME = 'person_form'
QUESTIONS_FORM_NAME = 'questions_form'
BUDGET_FORM_NAME = 'budget_form'
FUNDING_FORM_NAME = 'funding_form'
DATA_COLLECTION_FORM_NAME = 'data_collection_form'


class Homepage(TemplateView):
    template_name = 'homepage.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProposalThankYouView(TemplateView):
    template_name = 'proposal-thank_you.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        action = self.request.GET['action']

        if action in ('created', 'updated'):
            context['action'] = action
        else:
            # should not happen
            context['action'] = ''

        context['uuid'] = kwargs['uuid']

        return context


class ProposalTooLate(TemplateView):
    template_name = 'proposal-too_late.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        action = self.request.GET['action']

        context['action'] = action

        return context


class CallsList(TemplateView):
    template_name = 'call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.open_calls()

        return context


class ProposalDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        proposal = Proposal.objects.get(uuid=kwargs['uuid'])
        call = proposal.call

        context = call_context_for_template(call)

        context['proposal'] = proposal

        context['email'] = proposal.applicant.main_email()

        context['questions_answers'] = []

        for question in call.callquestion_set.all().order_by('order'):
            try:
                answer = ProposalQAText.objects.get(proposal=proposal, call_question=question).answer
            except ObjectDoesNotExist:
                answer = None

            question_text = question.question_text

            context['questions_answers'].append({'question': question_text,
                                                 'answer': answer})

        return render(request, 'proposal-detail.tmpl', context)


def call_context_for_template(call):
    context = {}
    context['maximum_budget'] = call.budget_maximum
    context['call_name'] = call.long_name
    context['call_introductory_message'] = call.introductory_message
    context['call_submission_deadline'] = call.submission_deadline
    context['other_funding_question'] = call.other_funding_question

    return context


class ProposalView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'uuid' in kwargs:
            proposal_uuid = kwargs['uuid']
            proposal: Proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME, instance=proposal)
            person_form = PersonForm(prefix=PERSON_FORM_NAME, person_position=proposal.applicant)
            questions_form = QuestionsForProposalForm(proposal=proposal,
                                                      prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)

            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME,
                                                      instance=proposal)
            data_collection_form = DataCollectionForm(prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)

            context['proposal_action_url'] = reverse('proposal-update', kwargs={'uuid': proposal.uuid})

            context['action'] = 'Edit'

        else:
            call_pk = context['call_pk'] = request.GET.get('call')
            call = Call.objects.get(pk=call_pk)

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(call=call,
                                                      prefix=QUESTIONS_FORM_NAME)

            initial_budget = []
            for budget_category in call.budget_categories.all():
                initial_budget.append({'category': budget_category, 'amount': None, 'details': None})

            budget_form = BudgetItemFormSet(call=call, prefix=BUDGET_FORM_NAME, initial=initial_budget)
            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME)
            data_collection_form = DataCollectionForm(prefix=DATA_COLLECTION_FORM_NAME)

            context['proposal_action_url'] = reverse('proposal-add')

            context['action'] = 'New'

        context.update(call_context_for_template(call))

        context[PROPOSAL_FORM_NAME] = proposal_form
        context[PERSON_FORM_NAME] = person_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form
        context[FUNDING_FORM_NAME] = funding_form
        context[DATA_COLLECTION_FORM_NAME] = data_collection_form

        return render(request, 'proposal-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'uuid' in kwargs:
            # Editing an existing proposal
            proposal_uuid = kwargs['uuid']
            proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call

            if timezone.now() > call.submission_deadline:
                return redirect(reverse('proposal-too-late') + '?action={}'.format('edited'))

        else:
            # New proposal
            call = Call.objects.get(id=int(request.POST['proposal_form-call_id']))

            if timezone.now() > call.submission_deadline:
                return redirect(reverse('proposal-too-late') + '?action={}'.format('edited'))

            proposal = None

        if proposal:
            # Editing an existing proposal
            proposal_form = ProposalForm(request.POST, instance=proposal, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, person_position=proposal.applicant, prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(request.POST,
                                                      proposal=proposal,
                                                      prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, proposal=proposal, prefix=BUDGET_FORM_NAME)
            funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME,
                                                      instance=proposal)
            data_collection_form = DataCollectionForm(request.POST,
                                                      prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)
            action = 'updated'

        else:
            # Creating a new proposal
            proposal_form = ProposalForm(request.POST, call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(request.POST,
                                                      call=call,
                                                      prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, prefix=BUDGET_FORM_NAME)
            funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME)
            data_collection_form = DataCollectionForm(request.POST, prefix=DATA_COLLECTION_FORM_NAME)

            action = 'created'

        forms_to_validate = [person_form, proposal_form, questions_form, budget_form,
                             funding_form, data_collection_form]

        all_valid = True
        for form in forms_to_validate:
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        if all_valid:
            applicant = person_form.save_person()
            data_collection_form.update(applicant)

            proposal = proposal_form.save(commit=False)
            proposal.applicant = applicant
            proposal.proposal_status = ProposalStatus.objects.get(name='Submitted')
            proposal.save()
            proposal_form.save(commit=True)

            funding_form.save_fundings(proposal)
            questions_form.save_answers(proposal)
            budget_form.save_budgets(proposal)

            return redirect(reverse('proposal-thank-you', kwargs={'uuid': proposal.uuid}) + '?action={}'.format(action))

        context[PERSON_FORM_NAME] = person_form
        context[PROPOSAL_FORM_NAME] = proposal_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form
        context[FUNDING_FORM_NAME] = funding_form
        context[DATA_COLLECTION_FORM_NAME] = data_collection_form

        context['action'] = 'Edit'

        context.update(call_context_for_template(call))

        messages.error(request, 'Proposal not saved. Please correct the errors in the form and try again')

        return render(request, 'proposal-form.tmpl', context)


class OrganisationsAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result):
        return result.long_name

    def get_queryset(self):
        qs = Organisation.objects.all()

        if self.q:
            qs = qs.filter(long_name__icontains=self.q)

        return qs


class KeywordsAutocomplete(autocomplete.Select2QuerySetView):
    def create_object(self, text):
        source, created = Source.objects.get_or_create(source='External User')

        keyword_uuid, created = KeywordUid.objects.get_or_create(uid=None, source=source)

        d = {self.create_field: text,
             'description': 'User entered',
             'uid': keyword_uuid}

        return self.get_queryset().get_or_create(
            **d)[0]

    def get_result_label(self, result):
        return result.name

    def get_queryset(self):
        qs = Keyword.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        qs = qs.order_by('name')
        return qs
