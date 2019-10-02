from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from .forms.proposal import PersonForm, ProposalForm, QuestionsForProposalForm, ProposalFundingItemFormSet, \
    BudgetItemFormSet
from .models import Proposal, Call, ProposalStatus, BudgetCategory

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


class CallsView(TemplateView):
    template_name = 'list_calls.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class ProposalThankYouView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['pk'] = kwargs['pk']

        return render(request, 'proposal-thank-you.tmpl', context)


class ProposalView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        information = {}

        if 'pk' in kwargs:
            proposal_pk = kwargs['pk']
            call = Proposal.objects.get(pk=kwargs['pk']).call

            proposal: Proposal = Proposal.objects.get(pk=proposal_pk)

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME, instance=proposal)
            person_form = PersonForm(prefix=PERSON_FORM_NAME, instance=proposal.applicant)
            questions_form = QuestionsForProposalForm(proposal=proposal,
                                                                                  prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)

            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME,
                                                                                       instance=proposal)

            information['proposal_action_url'] = reverse('proposal-update', kwargs={'pk': proposal_pk})

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

        information.update(ProposalView._call_information_for_template(call))

        information[PROPOSAL_FORM_NAME] = proposal_form
        information[PERSON_FORM_NAME] = person_form
        information[FUNDING_FORM_NAME] = funding_form
        information[QUESTIONS_FORM_NAME] = questions_form
        information[BUDGET_FORM_NAME] = budget_form

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

        proposal_pk = None

        if 'pk' in kwargs:
            proposal_pk = int(kwargs['pk'])
            call = Proposal.objects.get(pk=proposal_pk).call
        else:
            call = Call.objects.get(id=int(request.POST['proposal_form-call_id']))

        if proposal_pk:
            # Editing an existing proposal
            proposal = Proposal.objects.get(pk=proposal_pk)
            proposal_form = ProposalForm(request.POST, instance=proposal, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, instance=proposal.applicant, prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(request.POST,
                                                                   proposal=proposal,
                                                                   prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, proposal=proposal, prefix=BUDGET_FORM_NAME)
            funding_item_form_set = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME, instance=proposal)
        else:
            # Creating a new proposal
            proposal_form = ProposalForm(request.POST, call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, prefix=PERSON_FORM_NAME)
            questions_form = QuestionsForProposalForm(request.POST,
                                                                   call=call,
                                                                   prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, prefix=BUDGET_FORM_NAME)
            funding_item_form_set = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME)


        forms_to_validate = [person_form, proposal_form, questions_form, budget_form,
                             funding_item_form_set]

        all_valid = True
        for form in forms_to_validate:
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        if all_valid:
            applicant = person_form.save()

            proposal = proposal_form.save(commit=False)
            proposal.applicant = applicant
            proposal.proposal_status = ProposalStatus.objects.get(name='test01')
            proposal.save()
            proposal_form.save(commit=True)

            funding_item_form_set.save_fundings(proposal)
            questions_form.save_answers(proposal)
            budget_form.save_budgets(proposal)

            return redirect(reverse('proposal-thank-you', kwargs={'pk': proposal.pk}))

        context[PERSON_FORM_NAME] = person_form
        context[PROPOSAL_FORM_NAME] = proposal_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form
        context[FUNDING_FORM_NAME] = funding_item_form_set

        context.update(ProposalView._call_information_for_template(call))

        return render(request, 'proposal.tmpl', context)
