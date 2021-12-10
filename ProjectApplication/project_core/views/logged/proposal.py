import logging

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from ProjectApplication import settings
from comments.utils import process_comment_attachment
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.models import Reviewer, CallEvaluation
from project_core.models import Proposal, Call
from project_core.utils.utils import user_is_in_group_name
from project_core.views.common.proposal import AbstractProposalDetailView, AbstractProposalView
from project_core.views.common.proposal_parts import ProposalParts

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
                context['reviewer_calls_access'] = Reviewer.objects.get(user=self.request.user).\
                    calls_without_closed_call_evaluation()
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


class ProposalUpdateFiles(TemplateView):
    created_or_updated_url = ''
    form_template = ''
    action_url_add = ''
    action_url_update = ''
    success_message = ''

    extra_context = {}

    @staticmethod
    def _basic_context(proposal):
        breadcrumb = [
            {'name': 'Calls', 'url': reverse('logged-call-list')},
            {'name': f'List of proposals ({proposal.call.little_name()})',
             'url': reverse('logged-call-list-proposals', kwargs={'call_id': proposal.call.id})},
            {'name': f'Proposal ({proposal.applicant.person.full_name()})',
             'url': reverse('logged-proposal-detail', kwargs={'pk': proposal.pk})},
            {'name': 'Edit files'}
        ]

        return {'active_section': 'calls',
                'active_subsection': 'call-list',
                'sidebar_template': 'logged/_sidebar-calls.tmpl',
                'breadcrumb': breadcrumb,
                'form_action_url': reverse('logged-call-proposal-detail-update-files', kwargs={'pk': proposal.id}),
                'cancel_url': reverse('logged-proposal-detail', kwargs={'pk': proposal.pk})
                }

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        proposal = Proposal.objects.get(id=self.kwargs['pk'])

        context.update(ProposalUpdateFiles._basic_context(proposal))

        context['parts_with_answers'] = ProposalParts(None, None, proposal, only_files=True).get_forms()

        return render(request, 'logged/proposal-edit-files.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        proposal = Proposal.objects.get(id=kwargs['pk'])

        evaluation_started = CallEvaluation.objects.filter(call=proposal.call).exists()

        if evaluation_started:
            messages.error(request,
                           'Files cannot be changed because an evaluation for the call of this proposal has started')

            return redirect(reverse('logged-proposal-detail', kwargs={'pk': proposal.id}))

        parts_with_answers = ProposalParts(request.POST, request.FILES, proposal, only_files=True)

        all_valid = True

        for form in parts_with_answers.get_forms_only_files():
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        if all_valid is False:
            context.update(ProposalUpdateFiles._basic_context(proposal))
            context['parts_with_answers'] = parts_with_answers.get_forms()
            return render(request, 'logged/proposal-edit-files.tmpl', context)

        for question_form in parts_with_answers.get_forms_only_files():
            if not question_form.save_answers(proposal):
                messages.error(request,
                               'File attachments could not be saved - please try attaching the files again or contact an admin if the error reoccurs')

        messages.success(request, 'Files saved')

        return redirect(reverse('logged-proposal-detail', kwargs={'pk': proposal.id}))
