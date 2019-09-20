from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms import formset_factory
from .forms import proposal


class Homepage(TemplateView):
    template_name = 'homepage.tmpl'

    def get_context_data(self, **kwargs):
        context = super(Homepage, self).get_context_data(**kwargs)
        return context


class ProposalForm(TemplateView):
    template_name = 'proposal.tmpl'

    def get_context_data(self, **kwargs):
        context = super(ProposalForm, self).get_context_data(**kwargs)

        form = formset_factory(proposal.GeneralInformationForm)

        context['proposal_form'] = form

        return context
