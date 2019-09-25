from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse
from django.views.generic import TemplateView, CreateView
from django.forms import formset_factory
from .forms.proposal import PersonForm, ProposalForm, QuestionsForProposal, BudgetForm
from .models import Proposal, Call, Keyword, ProposalStatus, ProposalQAText
import re


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

            current_proposal: Proposal = Proposal.objects.get(pk=proposal_pk)

            information['proposal_form'] = ProposalForm(proposal_id=proposal_pk, prefix='proposal', instance=current_proposal)
            information['person_form'] = PersonForm(prefix='person', instance=current_proposal.applicant)
            information['questions_for_proposal_form'] = QuestionsForProposal(proposal_id=proposal_pk, prefix='questions_for_proposal')

            information['proposal_action_url'] = reverse('proposal-update', kwargs={'pk': proposal_pk})

        else:
            call_pk = information['call_pk'] = request.GET.get('call')
            call = Call.objects.get(pk=call_pk)

            information['proposal_form'] = ProposalForm(call_id=call_pk, prefix='proposal')
            information['person_form'] = PersonForm(prefix='person')
            information['questions_for_proposal_form'] = QuestionsForProposal(call_id=call_pk, prefix='questions_for_proposal')
            information['budget_form'] = BudgetForm(call_id=call_pk, prefix='budget')

            information['proposal_action_url'] = reverse('proposal-add')

        information['call_name'] = call.long_name
        information['call_introductory_message'] = call.introductory_message
        information['call_submission_deadline'] = call.submission_deadline

        return render(request, 'proposal.tmpl', information)

    def post(self, request, *args, **kwargs):
        context = super(ProposalView, self).get_context_data(**kwargs)

        person_form = PersonForm(request.POST, prefix='person')
        proposal_form = ProposalForm(request.POST, prefix='proposal')
        questions_for_proposal_form = QuestionsForProposal(request.POST,
                                                           call_id=request.POST['proposal-call_id'],
                                                           prefix='questions_for_proposal')

        if person_form.is_valid() and proposal_form.is_valid():
            call_id = proposal_form.cleaned_data['call_id']

            if questions_for_proposal_form.is_valid():
                applicant = person_form.save()
                proposal = proposal_form.save(commit=False)

                proposal.applicant = applicant
                proposal.call_id = call_id
                proposal.proposal_status = ProposalStatus.objects.get(name='test01')

                proposal = proposal_form.save(commit=True)

                for question, answer in questions_for_proposal_form.cleaned_data.items():
                    call_question_id = int(question[len('question_'):])

                    qa_text = ProposalQAText(proposal=proposal, call_question_id=call_question_id, answer=answer)
                    qa_text.save()

                for keyword_str in proposal_form.cleaned_data['keywords_str'].split(','):
                    keyword_str = keyword_str.strip(' ')
                    keyword = Keyword.objects.get_or_create(name=keyword_str)[0]
                    proposal.keywords.add(keyword)

                proposal.save()

                return redirect(reverse('proposal-thank-you', kwargs={'pk': proposal.pk}))

        context['person_form'] = person_form
        context['proposal_form'] = proposal_form
        context['questions_for_proposal_form'] = questions_for_proposal_form

        return render(request, 'proposal.tmpl', context)

#
# class Proposal(TemplateView):
#     template_name = 'proposal.tmpl'
#
#     def get(self, request, *args, **kwargs):
#         super(Proposal, self).get_context_data(**kwargs)
#
#         information = {}
#         call_pk = information['call_pk'] = request.GET.get('call')
#
#         call = Call.objects.get(pk=call_pk)
#
#         information['call_name'] = call.long_name
#         information['call_introductory_message'] = call.introductory_message
#         information['call_submission_deadline'] = call.submission_deadline
#         information['contact_form'] = proposal.PersonForm
#
#         return render(request, 'proposal.tmpl', information)
#
#     def post(self, request, *args, **kwargs):
#         form_class = proposal.PersonForm
#         form = form_class.get
