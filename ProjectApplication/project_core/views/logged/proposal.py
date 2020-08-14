import logging

from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView

from ProjectApplication import settings
from comments.utils import process_comment_attachment
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.models import Reviewer
from project_core.models import Proposal, Call
from project_core.utils.utils import user_is_in_group_name
from project_core.views.common.proposal import AbstractProposalDetailView, AbstractProposalView

logger = logging.getLogger('project_core')


def create_file_name(name_specification, call_id):
    if call_id is None:
        call_name = 'all'
    else:
        call = Call.objects.get(id=call_id)
        if call.short_name:
            call_name = call.short_name
        else:
            call_name = call.long_name

    date = timezone.now().strftime('%Y%m%d-%H%M%S')
    filename = name_specification.format(call_name.replace(' ', '_'), date)
    return filename


class ProposalList(ListView):
    template_name = 'logged/proposal-list.tmpl'
    model = Proposal
    context_object_name = 'proposals'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if user_is_in_group_name(self.request.user, settings.REVIEWER_GROUP_NAME):
            if hasattr(self.request.user, 'reviewer'):
                context['reviewer'] = self.request.user.reviewer.person
                context['reviewer_calls_access'] = Reviewer.objects.get(user=self.request.user).calls.all()
            else:
                messages.error(self.request,
                               'This review user is not setup properly. Contact SPI.')
                logger.warning(
                    f'NOTIFY: User in group reviewer but not having a reviewer associated: {self.request.user}')
                context['reviewer'] = f'User: {self.request.user.username}'

                context['reviewer_calls_access'] = []

            active_section = 'proposals'
            context['breadcrumb'] = [{'name': 'Proposals'}]
        else:
            active_section = 'lists'
            context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')}, {'name': 'Proposals'}]

        context.update({'active_section': active_section,
                        'active_subsection': 'proposal-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        return context

    def get_queryset(self):
        proposals = Proposal.objects.all()

        if user_is_in_group_name(self.request.user, settings.MANAGEMENT_GROUP_NAME):
            return proposals
        elif user_is_in_group_name(self.request.user, settings.REVIEWER_GROUP_NAME):
            return Reviewer.filter_proposals(proposals, self.request.user)
        else:
            assert False


class ProposalCommentAdd(AbstractProposalDetailView):
    def post(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'proposal-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        proposal = Proposal.objects.get(id=kwargs['pk'])

        result = process_comment_attachment(request, context, 'logged-proposal-detail', 'logged-proposal-comment-add',
                                            'logged/proposal-detail.tmpl',
                                            proposal)

        return result


def get_eligibility_history(proposal):
    current = proposal.history.first()

    eligibility_history = []

    if current:
        proposal_previous = current.prev_record

        eligibility_history.append(current)

        while proposal_previous:
            delta = current.diff_against(proposal_previous)
            eligibility_changed = False
            for change in delta.changes:
                eligibility_changed = eligibility_changed or change.field in ('eligibility', 'eligibility_comment')

            if eligibility_changed:
                eligibility_history.append(proposal_previous)

            current = proposal_previous
            proposal_previous = current.prev_record

    return eligibility_history


class ProposalDetailView(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            # When coming from adding comments/attachments it contains the 'id' but the
            # other system relies on the 'uuid'.
            # Adaptor here to avoid at all costs that the public page can use 'id' to refer to proposals
            # (even though the urls.py doesn't allow it...)
            proposal = Proposal.objects.get(id=kwargs['pk'])
            del kwargs['pk']
            kwargs['uuid'] = proposal.uuid
        elif 'uuid' in kwargs:
            # The normal proposal view from admin for example
            proposal = Proposal.objects.get(uuid=kwargs['uuid'])
        else:
            assert False

        context = self.prepare_context(request, *args, **kwargs)

        context[EligibilityDecisionForm.FORM_NAME] = EligibilityDecisionForm(prefix=EligibilityDecisionForm.FORM_NAME,
                                                                             proposal_id=proposal.id)

        context['eligibility_history'] = get_eligibility_history(proposal)

        return render(request, self.template, context)

    template = 'logged/proposal-detail.tmpl'

    extra_context = {'active_section': 'lists',
                     'active_subsection': 'proposal-list',
                     'sidebar_template': 'logged/_sidebar-lists.tmpl',
                     'breadcrumb': [{'name': 'Lists', 'url': reverse_lazy('logged-lists')},
                                    {'name': 'Proposals', 'url': reverse_lazy('logged-proposal-list')},
                                    {'name': 'Details'}]}


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'logged-proposal-detail'
    form_template = 'logged/form-proposal.tmpl'

    action_url_update = 'logged-proposal-update'
    action_url_add = 'logged-proposal-add'

    success_message = 'Proposal updated'

    extra_context = {'active_section': 'lists',
                     'active_subsection': 'proposal-list',
                     'sidebar_template': 'logged/_sidebar-lists.tmpl'}


class ProposalPreview(AbstractProposalView):
    preview = True
    form_template = 'common/form-proposal.tmpl'
