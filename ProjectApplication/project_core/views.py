from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms import formset_factory
from .forms import proposal
from .models import Call


class Homepage(TemplateView):
    template_name = 'homepage.tmpl'

    def get_context_data(self, **kwargs):
        context = super(Homepage, self).get_context_data(**kwargs)
        return context


class ProposalForm(TemplateView):
    pass


class Calls(TemplateView):
    template_name = 'list_calls.tmpl'

    def get_context_data(self, **kwargs):
        context = super(Calls, self).get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class Proposal(TemplateView):
    template_name = 'proposal.tmpl'

    def get(self, request, *args, **kwargs):
        context = super(Proposal, self).get_context_data(**kwargs)

        information = {}
        information['call_pk'] = request.GET.get('call')
        information['call_name'] = Call.objects.get(pk=information['call_pk'])

        return render(request, 'proposal.tmpl', information)
