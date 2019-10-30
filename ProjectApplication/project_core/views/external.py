from django.views.generic import TemplateView

from project_core.views.proposal import AbstractProposalDetailView, AbstractProposalView
from ..models import Call

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


class ProposalDetailView(AbstractProposalDetailView):
    template = 'proposal-detail.tmpl'


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'proposal-thank-you'
    form_template = 'proposal-form.tmpl'
    action_url_update = 'proposal-update'
    action_url_add = 'proposal-add'
