from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse

from ProjectApplication import settings
from evaluation.forms.proposal_evaluation import ProposalEvaluationForm
from project_core.models import Proposal
from project_core.utils import user_is_in_group_name
from project_core.views.common.proposal import AbstractProposalDetailView


def update_context(context, proposal_uuid):
    proposal = Proposal.objects.get(uuid=proposal_uuid)

    proposal_evaluation_form = ProposalEvaluationForm(prefix=ProposalEvaluationForm.FORM_NAME,
                                                      proposal=proposal)

    context[ProposalEvaluationForm.FORM_NAME] = proposal_evaluation_form

    context.update({'active_section': 'proposals',
                    'active_subsection': 'proposals-list',
                    'sidebar_template': 'logged/_sidebar-proposals.tmpl'})


class ProposalEvaluationDetail(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)
        update_context(context, kwargs['uuid'])

        return render(request, 'logged/proposal-detail-evaluation-detail.tmpl', context)


class ProposalEvaluationUpdate(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)
        update_context(context, kwargs['uuid'])

        return render(request, 'logged/proposal-detail-evaluation-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(uuid=kwargs['uuid'])

        proposal_evaluation_form = ProposalEvaluationForm(request.POST, prefix=ProposalEvaluationForm.FORM_NAME,
                                                          proposal=proposal)

        if proposal_evaluation_form.is_valid():
            proposal_evaluation_form.save(user=request.user)

            messages.success(request, 'Evaluation form saved')
            return redirect(reverse('logged-proposal-evaluation-detail', kwargs={'uuid': proposal.uuid}))
        else:
            messages.warning(request, 'Evaluation not saved. Verify errors in the form')
            context[ProposalEvaluationForm.FORM_NAME] = proposal_evaluation_form

            context.update({'active_section': 'proposals',
                            'active_subsection': 'proposals-list',
                            'sidebar_template': 'logged/_sidebar-proposals.tmpl'})

            return render(request, 'logged/proposal-detail-evaluation-form.tmpl', context)
