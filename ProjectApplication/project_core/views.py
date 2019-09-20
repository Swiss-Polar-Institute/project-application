from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.forms import formset_factory
from .forms.proposal import PersonForm, ProposalForm
from .models import Proposal, Call


class Homepage(TemplateView):
    template_name = 'homepage.tmpl'

    def get_context_data(self, **kwargs):
        context = super(Homepage, self).get_context_data(**kwargs)
        return context


class Calls(TemplateView):
    template_name = 'list_calls.tmpl'

    def get_context_data(self, **kwargs):
        context = super(Calls, self).get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class Proposal(TemplateView):
    def get(self, request, *args, **kwargs):
        super(Proposal, self).get_context_data(**kwargs)

        information = {}
        call_pk = information['call_pk'] = request.GET.get('call')

        call = Call.objects.get(pk=call_pk)

        information['call_name'] = call.long_name
        information['call_introductory_message'] = call.introductory_message
        information['call_submission_deadline'] = call.submission_deadline

        information['person_form'] = PersonForm()
        information['proposal_form'] = ProposalForm()

        return render(request, 'proposal.tmpl', information)

    def post(self, request, *args, **kwargs):
        super(Proposal, self).get_context_data(**kwargs)

        person_form = PersonForm(request.POST)
        proposal_form = ProposalForm(request.POST)

        if person_form.is_valid() and proposal_form.is_valid():
            applicant = person_form.save()
            proposal_form.applicant = applicant

        print('hello')

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
