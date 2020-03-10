from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from ProjectApplication import settings
from comments.utils import process_comment_attachment
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.models import Reviewer
from project_core.models import Proposal, Call
from project_core.utils import user_is_in_group_name
from project_core.views.common.proposal import AbstractProposalDetailView, AbstractProposalView


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


class ProposalsList(TemplateView):
    template_name = 'logged/proposal-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        call_id = self.request.GET.get('call', None)

        context['proposals'] = Proposal.objects.all()

        if call_id:
            call = context['call_filter'] = Call.objects.get(id=call_id)
            context['proposals'] = context['proposals'].filter(call=call)

        if user_is_in_group_name(self.request.user, settings.REVIEWER_GROUP_NAME):
            context['reviewer'] = self.request.user
            context['proposals'] = Reviewer.filter_proposals(context['proposals'], self.request.user)
            context['reviewer_calls_access'] = Reviewer.objects.get(user=self.request.user).calls.all()

        context.update({'active_section': 'lists',
                        'active_subsection': 'proposals-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        return context


class ProposalEligibilityUpdate(AbstractProposalDetailView):
    def post(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)

        proposal_uuid = kwargs['uuid']

        eligibility_decision_form = EligibilityDecisionForm(request.POST, prefix=EligibilityDecisionForm.FORM_NAME,
                                                            proposal_uuid=proposal_uuid)

        if eligibility_decision_form.is_valid():
            eligibility_decision_form.save_eligibility(request.user)

            messages.success(request, 'Eligibility saved')
            return redirect(reverse('logged-proposal-detail', kwargs={'uuid': proposal_uuid}))

        else:
            messages.warning(request, 'Eligibility not saved. Verify errors in the form')
            context[EligibilityDecisionForm.FORM_NAME] = eligibility_decision_form

            context.update({'active_section': 'proposals',
                            'active_subsection': 'proposals-list',
                            'sidebar_template': 'logged/_sidebar-proposals.tmpl'})

            return render(request, 'logged/proposal-detail.tmpl', context)


class ProposalCommentAdd(AbstractProposalDetailView):
    def post(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        context.update({'active_section': 'proposals',
                        'active_subsection': 'proposals-list',
                        'sidebar_template': 'logged/_sidebar-proposals.tmpl'})

        proposal = Proposal.objects.get(id=kwargs['id'])

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
        if 'id' in kwargs:
            # When coming from adding comments/attachments it contains the 'id' but the
            # other system relies on the 'uuid'.
            # Adaptor here to avoid at all costs that the public page can use 'id' to refer to proposals
            # (even though the urls.py doesn't allow it...)
            proposal = Proposal.objects.get(id=kwargs['id'])
            del kwargs['id']
            kwargs['uuid'] = proposal.uuid
        elif 'uuid' in kwargs:
            # The normal proposal view from admin for example
            proposal = Proposal.objects.get(uuid=kwargs['uuid'])
        else:
            assert False

        context = self.prepare_context(request, *args, **kwargs)

        context[EligibilityDecisionForm.FORM_NAME] = EligibilityDecisionForm(prefix=EligibilityDecisionForm.FORM_NAME,
                                                                             proposal_uuid=proposal.uuid)

        context['eligibility_history'] = get_eligibility_history(proposal)

        return render(request, self.template, context)

    template = 'logged/proposal-detail.tmpl'

    extra_context = {'active_section': 'proposals',
                     'active_subsection': 'proposals-list',
                     'sidebar_template': 'logged/_sidebar-proposals.tmpl'}


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'logged-proposal-detail'
    form_template = 'logged/proposal-form.tmpl'

    action_url_update = 'logged-proposal-update'
    action_url_add = 'logged-proposal-add'

    success_message = 'Proposal updated'

    extra_context = {'active_section': 'proposals',
                     'active_subsection': 'proposals-list',
                     'sidebar_template': 'logged/_sidebar-proposals.tmpl'}
