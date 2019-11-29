from django.views.generic import TemplateView

from project_core.views.common.proposal import AbstractProposalDetailView, AbstractProposalView
from project_core.models import Proposal


class ProposalThankYouView(TemplateView):
    template_name = 'external/proposal-thank_you.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['proposal'] = Proposal.objects.get(uuid=kwargs['uuid'])

        return context


class ProposalTooLate(TemplateView):
    template_name = 'external/proposal-too_late.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        action = self.request.GET['action']

        context['action'] = action

        return context


class ProposalDetailView(AbstractProposalDetailView):
    template = 'external/proposal-detail.tmpl'


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'proposal-thank-you'
    form_template = 'common/proposal-form.tmpl'
    action_url_update = 'proposal-update'
    action_url_add = 'proposal-add'
