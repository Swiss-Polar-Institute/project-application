from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from .forms.proposal import PersonForm, ProposalForm, QuestionsForProposalForm, ProposalFundingItemFormSet, \
    BudgetItemFormSet, budget_form_factory
from .models import Proposal, Call, ProposalStatus, BudgetCategory


class Homepage(TemplateView):
    template_name = 'homepage.tmpl'

    def get_context_data(self, **kwargs):
        context = super(Homepage, self).get_context_data(**kwargs)
        return context


class CallsView(TemplateView):
    template_name = 'list_calls.tmpl'

    def get_context_data(self, **kwargs):
        context = super(CallsView, self).get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class ProposalThankYouView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super(ProposalThankYouView, self).get_context_data(**kwargs)

        context['pk'] = kwargs['pk']

        return render(request, 'proposal-thank-you.tmpl', context)


class ProposalView(TemplateView):
    def get(self, request, *args, **kwargs):
        super(ProposalView, self).get_context_data(**kwargs)

        information = {}

        if 'pk' in kwargs:
            proposal_pk = kwargs['pk']
            call = Proposal.objects.get(pk=kwargs['pk']).call

            proposal: Proposal = Proposal.objects.get(pk=proposal_pk)

            information['proposal_form'] = ProposalForm(call=call, prefix='proposal', instance=proposal)
            information['person_form'] = PersonForm(prefix='person', instance=proposal.applicant)

            information['funding'] = ProposalFundingItemFormSet(prefix='funding',
                                                                                       instance=proposal)

            information['questions_for_proposal_form'] = QuestionsForProposalForm(proposal=proposal,
                                                                                  prefix='questions_for_proposal')
            information['budget_form'] = BudgetItemFormSet(proposal=proposal, prefix='budget')

            information['proposal_action_url'] = reverse('proposal-update', kwargs={'pk': proposal_pk})

        else:
            call_pk = information['call_pk'] = request.GET.get('call')
            call = Call.objects.get(pk=call_pk)

            information['proposal_form'] = ProposalForm(call=call, prefix='proposal')
            information['person_form'] = PersonForm(prefix='person')

            information['funding'] = ProposalFundingItemFormSet(prefix='funding')

            information['questions_for_proposal_form'] = QuestionsForProposalForm(call=call,
                                                                                  prefix='questions_for_proposal')

            initial_budget = []
            for budget_category in call.budget_categories.all():
                initial_budget.append({'category': budget_category, 'amount': None, 'details': None})

            information['budget_form'] = BudgetItemFormSet(call=call, prefix='budget', initial=initial_budget)
            information['proposal_action_url'] = reverse('proposal-add')

        information.update(ProposalView._call_information_for_template(call))

        print(information['budget_form'])
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
        context = super(ProposalView, self).get_context_data(**kwargs)

        proposal_pk = None

        if 'pk' in kwargs:
            proposal_pk = int(kwargs['pk'])
            call = Proposal.objects.get(pk=proposal_pk).call
        else:
            call = Call.objects.get(id=int(request.POST['proposal-call_id']))

        if proposal_pk is None:
            # It's a new Proposal
            person_form = PersonForm(request.POST, prefix='person')
            proposal_form = ProposalForm(request.POST, call=call, prefix='proposal')
            questions_for_proposal_form = QuestionsForProposalForm(request.POST,
                                                                   call=call,
                                                                   prefix='questions_for_proposal')
            budget_form = BudgetItemFormSet(request.POST, call=call, prefix='budget')
            funding_item_form_set = ProposalFundingItemFormSet(request.POST, prefix='funding')
        else:
            # It needs to modify an existing Proposal
            proposal = Proposal.objects.get(pk=proposal_pk)

            person_form = PersonForm(request.POST, instance=proposal.applicant, prefix='person')
            proposal_form = ProposalForm(request.POST, instance=proposal, prefix='proposal')
            questions_for_proposal_form = QuestionsForProposalForm(request.POST,
                                                                   proposal=proposal,
                                                                   prefix='questions_for_proposal')
            budget_form = BudgetItemFormSet(request.POST, call=call, proposal=proposal, prefix='budget')
            funding_item_form_set = ProposalFundingItemFormSet(request.POST, prefix='funding', instance=proposal)

        # TODO do it in a loop...
        person_form_is_valid = person_form.is_valid()
        proposal_form_is_valid = proposal_form.is_valid()
        questions_for_proposal_form_is_valid = questions_for_proposal_form.is_valid()
        budget_form_is_valid = budget_form.is_valid()
        funding_item_form_set_is_valid = funding_item_form_set.is_valid()

        if person_form_is_valid and proposal_form_is_valid and questions_for_proposal_form_is_valid and budget_form_is_valid and funding_item_form_set_is_valid:
            applicant = person_form.save()
            proposal = proposal_form.save(commit=False)

            proposal.applicant = applicant

            proposal.proposal_status = ProposalStatus.objects.get(name='test01')

            funding_items = funding_item_form_set.save(commit=False)

            proposal = proposal_form.save(commit=True)
            proposal.save()

            for funding_item in funding_items:
                funding_item.proposal = proposal
                funding_item.save()

            questions_for_proposal_form._proposal_id = proposal.pk
            questions_for_proposal_form.save_answers()

            proposal.save()

            for budget_item_form in budget_form:
                budget_item_form.save_budget(proposal)

            return redirect(reverse('proposal-thank-you', kwargs={'pk': proposal.pk}))

        context['person_form'] = person_form
        context['proposal_form'] = proposal_form
        context['questions_for_proposal_form'] = questions_for_proposal_form
        context['budget_form'] = budget_form
        context['funding'] = funding_item_form_set

        print(funding_item_form_set)

        context.update(ProposalView._call_information_for_template(call))

        return render(request, 'proposal.tmpl', context)
