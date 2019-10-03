from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from ..models import Proposal
from django.shortcuts import render, redirect


class ProposalsList(TemplateView):
    template_name = 'internal/list_proposals.tmpl'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['proposals'] = Proposal.objects.all()

        return context


class InternalHomepage(TemplateView):
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        return render(request, 'internal/homepage.tmpl', context)


class CallView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        return render(request, 'internal/call.tmpl', {})
