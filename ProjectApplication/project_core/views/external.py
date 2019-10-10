from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from dal import autocomplete

from ..forms.proposal import PersonForm, ProposalForm, QuestionsForProposalForm, ProposalFundingItemFormSet, \
    BudgetItemFormSet
from ..models import Proposal, Call, ProposalStatus, Organisation, Keyword

# Form names (need to match what's in the templates)
PROPOSAL_FORM_NAME = 'proposal_form'
PERSON_FORM_NAME = 'person_form'
QUESTIONS_FORM_NAME = 'questions_form'
BUDGET_FORM_NAME = 'budget_form'
FUNDING_FORM_NAME = 'funding_form'


class Homepage(TemplateView):
    template_name = 'homepage.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProposalThankYouView(TemplateView):
    template_name = 'proposal-thank_you.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['uuid'] = kwargs['uuid']

        return context


class CallsList(TemplateView):
    template_name = 'call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class ProposalView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        information = {}

        if 'uuid' in kwargs:
            proposal_uuid = kwargs['uuid']
            proposal: Proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME, instance=proposal)
            person_form = PersonForm(prefix=PERSON_FORM_NAME, instance=proposal.applicant)
            questions_form = QuestionsForProposalForm(proposal=proposal,
                                                      prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)

            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME,
                                                      instance=proposal)

            information['proposal_action_url'] = reverse('proposal-update', kwargs={'uuid': proposal.uuid})

            information['action'] = 'Edit'

        else:
            call_pk = information['call_pk'] = request.GET.get('call')
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

            information['proposal_action_url'] = reverse('proposal-add')

            information['action'] = 'New'

        information.update(ProposalView._call_information_for_template(call))

        information[PROPOSAL_FORM_NAME] = proposal_form
        information[PERSON_FORM_NAME] = person_form
        information[CONTACT_FORM_NAME] = contact_form
        information[QUESTIONS_FORM_NAME] = questions_form
        information[BUDGET_FORM_NAME] = budget_form
        information[FUNDING_FORM_NAME] = funding_form

        return render(request, 'proposal.tmpl', information)

    @staticmethod
    def _call_information_for_template(call):
        information = {}
        information['maximum_budget'] = call.budget_maximum
        information['call_name'] = call.long_name
        information['call_introductory_message'] = call.introductory_message
        information['call_submission_deadline'] = call.submission_deadline

        return information

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'uuid' in kwargs:
            proposal_uuid = kwargs['uuid']
            proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call
        else:
            call = Call.objects.get(id=int(request.POST['proposal_form-call_id']))
            proposal = None

        if proposal:
            # Editing an existing proposal
            proposal_form = ProposalForm(request.POST, instance=proposal, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, instance=proposal.applicant, prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(request.POST,
                                                      proposal=proposal,
                                                      prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, proposal=proposal, prefix=BUDGET_FORM_NAME)
            funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME,
                                                               instance=proposal)
        else:
            # Creating a new proposal
            proposal_form = ProposalForm(request.POST, call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(request.POST,
                                                      call=call,
                                                      prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, prefix=BUDGET_FORM_NAME)
            funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME)

        forms_to_validate = [person_form, contact_form, proposal_form, questions_form, budget_form,
                             funding_form]

        all_valid = True
        for form in forms_to_validate:
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        if all_valid:
            applicant = person_form.save()

            contact = contact_form.save(commit=False)
            contact.person = applicant
            contact.save()

            proposal = proposal_form.save(commit=False)
            proposal.applicant = applicant
            proposal.proposal_status = ProposalStatus.objects.get(name='test01')
            proposal.save()
            proposal_form.save(commit=True)

            funding_form.save_fundings(proposal)
            questions_form.save_answers(proposal)
            budget_form.save_budgets(proposal)

            return redirect(reverse('proposal-thank-you', kwargs={'uuid': proposal.uuid}))

        context[PERSON_FORM_NAME] = person_form
        context[CONTACT_FORM_NAME] = contact_form
        context[PROPOSAL_FORM_NAME] = proposal_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form
        context[FUNDING_FORM_NAME] = funding_form

        context['action'] = 'Edit'

        context.update(ProposalView._call_information_for_template(call))

        return render(request, 'proposal.tmpl', context)


class OrganisationsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Organisation.objects.all()

        if self.q:
            qs = qs.filter(long_name__contains=self.q)

        return qs


class KeywordsAutocomplete(autocomplete.Select2QuerySetView):
    def create_object(self, text):
        d = {self.create_field: text,
             'description': 'user entered'}

        return self.get_queryset().get_or_create(
            **d)[0]

    def get_result_label(self, result):
        return result.name

    def get_queryset(self):
        qs = Keyword.objects.all()

        if self.q:
            qs = qs.filter(name__contains=self.q)

        return qs