from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models.fields.files import FieldFile
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, ListView, DetailView

from ProjectApplication import settings
from comments import utils
from comments.utils import comments_attachments_forms, process_comment_attachment
from evaluation.forms.call_evaluation import CallEvaluationForm
from evaluation.forms.close_call_evaluation import CloseCallEvaluation
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.forms.proposal_evaluation import ProposalEvaluationForm
from evaluation.models import CallEvaluation, ProposalEvaluation
from project_core.models import Proposal, Call, ProposalStatus
from project_core.utils.utils import user_is_in_group_name
from project_core.views.common.proposal import AbstractProposalDetailView
from project_core.views.logged.proposal import get_eligibility_history


def add_proposal_evaluation_form(context, proposal):
    proposal_evaluation_form = ProposalEvaluationForm(prefix=ProposalEvaluationForm.FORM_NAME,
                                                      proposal=proposal)

    context[ProposalEvaluationForm.FORM_NAME] = proposal_evaluation_form


class ProposalEvaluationDetail(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        proposal_evaluation_id = kwargs['pk']
        proposal_evaluation = ProposalEvaluation.objects.get(id=proposal_evaluation_id)

        context = self.prepare_context(request, *args, **{'pk': proposal_evaluation.proposal.id})
        add_proposal_evaluation_form(context, proposal_evaluation.proposal)

        context.update(comments_attachments_forms('logged-proposal-evaluation-comment-add', proposal_evaluation))

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'List of proposals ({proposal_evaluation.proposal.call.little_name()})',
                                  'url': reverse('logged-call-evaluation-list-proposals',
                                                 kwargs={'call_id': proposal_evaluation.proposal.call.id})},
                                 {'name': 'Proposal evaluation'}]

        return render(request, 'logged/proposal-detail-evaluation-detail.tmpl', context)


class ProposalEvaluationList(TemplateView):
    template_name = 'evaluation/call_evaluation-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls_opened_evaluation'] = Call.closed_calls().filter(callevaluation__closed_date__isnull=True)
        context['calls_closed_evaluation'] = Call.closed_calls().filter(callevaluation__closed_date__isnull=False)

        context['proposals_no_draft_only'] = True

        context.update({'view_button': False,
                        'edit_button': False,
                        'proposal_call_list_button': False,
                        'proposal_evaluation_list_button': True,
                        'evaluation_spreadsheet_button': True,
                        'view_evaluation_button': True,
                        'evaluation_summary_or_validation_button': True
                        })

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls to evaluate'}]

        return context


class ProposalEvaluationUpdate(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied(f'User {request.user} does not have access to Evaluate proposals')

        if 'pk' in kwargs:
            proposal_evaluation = ProposalEvaluation.objects.get(id=kwargs['pk'])
            proposal = proposal_evaluation.proposal
        elif 'proposal' in request.GET:
            proposal_id = request.GET['proposal']
            proposal = Proposal.objects.get(id=proposal_id)
        else:
            assert False

        if proposal.call.callevaluation.is_closed():
            raise PermissionDenied('Cannot edit a Proposal Evaluation for a closed call')

        context = self.prepare_context(request, *args, **{'pk': proposal.id})

        add_proposal_evaluation_form(context, proposal)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'List of proposals ({proposal.call.short_name})',
                                  'url': reverse('logged-call-evaluation-list-proposals',
                                                 kwargs={'call_id': proposal.call.id})},
                                 {'name': 'Edit proposal evaluation'}]

        return render(request, 'logged/proposal-detail-evaluation-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied('User does not have access to update a Proposal')

        proposal = Proposal.objects.get(id=kwargs['pk'])

        if proposal.call.callevaluation.is_closed():
            raise PermissionDenied('Cannot edit a Proposal Evaluation for a closed call')

        context = self.prepare_context(request, *args, **kwargs)

        proposal_evaluation_form = ProposalEvaluationForm(request.POST, request.FILES,
                                                          prefix=ProposalEvaluationForm.FORM_NAME,
                                                          proposal=proposal)

        if proposal_evaluation_form.is_valid():
            proposal_evaluation = proposal_evaluation_form.save(user=request.user)

            messages.success(request, 'Evaluation saved')
            return redirect(reverse('logged-proposal-evaluation-detail', kwargs={'pk': proposal_evaluation.id}))
        else:
            messages.error(request, 'Evaluation not saved. Verify errors in the form.')
            context[ProposalEvaluationForm.FORM_NAME] = proposal_evaluation_form

            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            return render(request, 'logged/proposal-detail-evaluation-form.tmpl', context)


class CallEvaluationUpdate(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'pk' in kwargs:
            call_evaluation = CallEvaluation.objects.get(id=kwargs['pk'])
            call = call_evaluation.call
        else:
            call_evaluation = None
            call = Call.objects.get(id=self.request.GET['call'])

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['call'] = call

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': 'Edit call evaluation'}]

        call_evaluation_form = CallEvaluationForm(instance=call_evaluation, prefix=CallEvaluationForm.FORM_NAME,
                                                  call=call)

        context[CallEvaluationForm.FORM_NAME] = call_evaluation_form

        return render(request, 'evaluation/call_evaluation-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        context = super().get_context_data(**kwargs)

        if 'pk' in kwargs:
            call_evaluation = CallEvaluation.objects.get(id=kwargs['pk'])
            call = call_evaluation.call
        else:
            call_evaluation = None
            call = Call.objects.get(id=self.request.GET['call'])

        call_evaluation_form = CallEvaluationForm(request.POST, request.FILES, instance=call_evaluation,
                                                  prefix=CallEvaluationForm.FORM_NAME, call=call)

        if call_evaluation_form.is_valid():
            call_evaluation = call_evaluation_form.save_call_evaluation(user=request.user)

            messages.success(request, 'Call evaluation saved')
            return redirect(reverse('logged-call-evaluation-detail', kwargs={'pk': call_evaluation.id}))
        else:
            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            messages.error(request, 'Call evaluation not saved. Verify errors in the form.')
            context[CallEvaluationForm.FORM_NAME] = call_evaluation_form

            context['call'] = call

            return render(request, 'evaluation/call_evaluation-form.tmpl', context)


class ProposalList(ListView):
    template_name = 'evaluation/call_evaluation_list-proposals.tmpl'
    model = Proposal
    context_object_name = 'proposals'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=self.kwargs['call_id'])

        context['call'] = call

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'List of proposals ({call.little_name()})'}]

        return context

    def get_queryset(self):
        call = Call.objects.get(id=self.kwargs['call_id'])
        draft = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_DRAFT)
        proposals = Proposal.objects.filter(call=call).exclude(proposal_status=draft)

        return proposals


class CallEvaluationDetail(DetailView):
    model = CallEvaluation
    template_name = 'evaluation/call_evaluation-detail.tmpl'
    context_object_name = 'call_evaluation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': 'View call evaluation'}]

        call_evaluation = CallEvaluation.objects.get(id=self.kwargs['pk'])

        context.update(comments_attachments_forms('logged-call-evaluation-comment-add', call_evaluation))

        return context


class CallEvaluationCommentAdd(TemplateView):
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        call_evaluation = CallEvaluation.objects.get(id=kwargs['pk'])

        result = process_comment_attachment(request, context, 'logged-call-evaluation-detail',
                                            'logged-proposal-call-comment-add',
                                            'logged/call-evaluation-detail.tmpl',
                                            call_evaluation)

        return result


def proposal_detail_eligibility_context(proposal):
    context = {}
    context.update(utils.comments_attachments_forms('logged-call-evaluation-proposal-detail', proposal))

    context.update({'active_section': 'evaluation',
                    'active_subsection': 'evaluation-list',
                    'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'
                    })

    context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                             {'name': f'List of proposals ({proposal.call.short_name})',
                              'url': reverse('logged-call-evaluation-list-proposals',
                                             kwargs={'call_id': proposal.call.id})},
                             {'name': 'Proposal'}]

    context[EligibilityDecisionForm.FORM_NAME] = EligibilityDecisionForm(prefix=EligibilityDecisionForm.FORM_NAME,
                                                                         proposal_id=proposal.id)

    context['eligibility_history'] = get_eligibility_history(proposal)

    return context


class ProposalDetail(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(id=kwargs['pk'])

        context.update(proposal_detail_eligibility_context(proposal))

        context['force_eligibility_form_displayed'] = True

        return render(request, 'evaluation/proposal-detail.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        proposal = Proposal.objects.get(id=kwargs['pk'])

        result = process_comment_attachment(request, context, 'logged-call-evaluation-proposal-detail',
                                            'logged-call-comment-add',
                                            'logged/proposal-detail.tmpl',
                                            proposal)

        return result


class ProposalCommentAdd(TemplateView):
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'logged/_sidebar-evaluation.tmpl'})

        proposal_evaluation = ProposalEvaluation.objects.get(id=kwargs['pk'])

        result = process_comment_attachment(request, context, 'logged-proposal-evaluation-detail',
                                            'logged-proposal-evaluation-comment-add',
                                            'logged/proposal-evaluation-detail.tmpl',
                                            proposal_evaluation)

        return result


class ProposalEligibilityUpdate(AbstractProposalDetailView):
    def post(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)

        proposal_id = kwargs['pk']

        eligibility_decision_form = EligibilityDecisionForm(request.POST, prefix=EligibilityDecisionForm.FORM_NAME,
                                                            proposal_id=proposal_id)

        if eligibility_decision_form.is_valid():
            eligibility_decision_form.save_eligibility(request.user)

            messages.success(request, 'Eligibility saved')
            return redirect(reverse('logged-call-evaluation-proposal-detail', kwargs={'pk': proposal_id}))

        else:
            messages.error(request, 'Eligibility not saved. Verify errors in the form.')

            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            proposal = Proposal.objects.get(id=proposal_id)

            context.update(proposal_detail_eligibility_context(proposal))

            context[EligibilityDecisionForm.FORM_NAME] = eligibility_decision_form

            context['force_eligibility_form_displayed'] = True

            return render(request, 'evaluation/proposal-detail.tmpl', context)


class CallEvaluationSummary(TemplateView):
    template_name = 'evaluation/call_evaluation-summary-detail.tmpl'

    @staticmethod
    def get_call_summary(call):
        summary = {}
        proposals = Proposal.objects.filter(call=call)

        submitted_status = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_SUBMITTED)
        summary['total_number_of_submitted'] = proposals.filter(proposal_status=submitted_status).count()
        summary['total_number_of_eligible'] = proposals.filter(eligibility=Proposal.ELIGIBLE).count()
        summary['total_number_of_funded'] = proposals.filter(
            proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_FUND).count()
        summary['total_number_of_eligible_not_funded'] = summary['total_number_of_eligible'] - summary[
            'total_number_of_funded']

        return summary

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])

        context['call'] = call

        context.update(CallEvaluationSummary.get_call_summary(call))

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'Evaluation summary ({call.little_name()})'}]

        return context


class CallEvaluationValidation(TemplateView):
    template_name = 'evaluation/call_evaluation-validation-detail.tmpl'

    @staticmethod
    def _all_good(checks):
        all_good = True
        for check in checks:
            all_good = all_good and check['ok']

        return all_good

    @staticmethod
    def _add_call_evaluation_proposal_detail_url(proposals):
        for proposal in proposals:
            proposal.url_fix_validation_error = reverse('logged-call-evaluation-proposal-detail',
                                                        kwargs={'pk': proposal.id})

    @staticmethod
    def _add_call_evaluation_proposal_evaluation_edit_url(proposals):
        proposal: Proposal
        for proposal in proposals:
            if hasattr(proposal, 'proposalevaluation'):
                proposal.url_fix_validation_error = reverse('logged-proposal-evaluation-update',
                                                            kwargs={'pk': proposal.proposalevaluation.pk})
            else:
                # Actually logged-proposale-valuation-add also works if the proposal-evaluation is already created -
                # we could use this one only if needed
                proposal.url_fix_validation_error = reverse(
                    'logged-proposal-evaluation-add') + f'?proposal={proposal.id}'

    @staticmethod
    def _check_call_evaluation_is_completed(call_evaluation):
        required_fields = CallEvaluationForm(call=call_evaluation.call).fields
        del required_fields['reviewers']  # reviewers is required but it's checked on the form
        # below check using getattr would always fail because
        # it's a Many to Many

        missing_fields = []

        for required_field in required_fields:
            value = getattr(call_evaluation, required_field)

            if (type(value) == FieldFile and bool(value) is False) or (value is None):
                missing_fields.append(required_fields[required_field].label)

        edit_link = reverse('logged-call-evaluation-update', kwargs={'pk': call_evaluation.pk})
        return {
            'message_all_good': 'Call Evaluation details have been completed',
            'message_problem': mark_safe(
                f'Missing fields in the call evaluation: <em>{",".join(missing_fields)}</em>. <a href="{edit_link}">Edit Call Evaluation</a>'),
            'ok': len(missing_fields) == 0
        }

    @staticmethod
    def _check_all_submitted_proposals_have_eligibility_set(proposals):
        proposals_without_eligibility_set = proposals.filter(
            proposal_status__name=settings.PROPOSAL_STATUS_SUBMITTED).filter(eligibility=Proposal.ELIGIBILITYNOTCHECKED)

        proposals_without_eligibility_set = proposals_without_eligibility_set.order_by('id')

        CallEvaluationValidation._add_call_evaluation_proposal_detail_url(
            proposals_without_eligibility_set)

        return {'message_problem': 'Not all submitted proposals have had their eligibility checked',
                'message_all_good': 'All submitted proposals have had their eligibility checked',
                'ok': proposals_without_eligibility_set.count() == 0,
                'proposals': proposals_without_eligibility_set}

    @staticmethod
    def _check_proposal_evaluations_have_letter_for_applicant(proposals):
        proposals_with_decision_letter = proposals.exclude(proposalevaluation__decision_letter='').values_list('id',
                                                                                                               flat=True)
        proposals_without_decision_letter = proposals.exclude(id__in=proposals_with_decision_letter)

        proposals_without_decision_letter = proposals_without_decision_letter.order_by('id')

        CallEvaluationValidation._add_call_evaluation_proposal_evaluation_edit_url(proposals_without_decision_letter)

        return {'message_problem': 'There are proposals without a decision letter',
                'message_all_good': 'All the proposals have a decision letter',
                'ok': proposals_without_decision_letter.count() == 0,
                'proposals': proposals_without_decision_letter}

    @staticmethod
    def _check_all_proposals_decision_panel_set(proposals):
        proposals_with_panel_recommendation = proposals.filter(
            proposalevaluation__panel_recommendation__isnull=False).values_list('id', flat=True)

        proposals_without_panel_recommendation = proposals.exclude(id__in=proposals_with_panel_recommendation)

        proposals_without_panel_recommendation = proposals_without_panel_recommendation.order_by('id')

        CallEvaluationValidation._add_call_evaluation_proposal_evaluation_edit_url(
            proposals_without_panel_recommendation)

        return {'message_problem': 'There are proposals without a panel recommendation',
                'message_all_good': 'All the proposals have a panel recommendation',
                'ok': proposals_without_panel_recommendation.count() == 0,
                'proposals': proposals_without_panel_recommendation}

    @staticmethod
    def _check_all_proposals_board_meeting_set(proposals):
        proposals_with_board_meeting_set = proposals.filter(
            proposalevaluation__board_decision__isnull=False).values_list('id', flat=True)

        proposals_without_board_meeting_decision = proposals.exclude(id__in=proposals_with_board_meeting_set)

        proposals_without_board_meeting_decision = proposals_without_board_meeting_decision.order_by('id')

        CallEvaluationValidation._add_call_evaluation_proposal_evaluation_edit_url(
            proposals_without_board_meeting_decision)

        return {'message_problem': 'There are proposals without a board decision',
                'message_all_good': 'All the proposals have a board decision',
                'ok': proposals_without_board_meeting_decision.count() == 0,
                'proposals': proposals_without_board_meeting_decision}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])

        proposals = Proposal.objects.filter(call=call)
        eligible_proposals = proposals.filter(eligibility=Proposal.ELIGIBLE)

        proposal_validations = []
        proposal_validations.append(self._check_all_submitted_proposals_have_eligibility_set(proposals))

        evaluation_validations = []
        evaluation_validations.append(self._check_proposal_evaluations_have_letter_for_applicant(eligible_proposals))
        evaluation_validations.append(self._check_all_proposals_decision_panel_set(eligible_proposals))
        evaluation_validations.append(self._check_all_proposals_board_meeting_set(eligible_proposals))
        evaluation_validations.append(self._check_call_evaluation_is_completed(call.callevaluation))

        context['proposal_validations'] = proposal_validations
        context['evaluation_validations'] = evaluation_validations

        context['call'] = call

        context['all_good'] = CallEvaluationValidation._all_good(proposal_validations + evaluation_validations)
        context['can_close'] = context['all_good'] and call.callevaluation.closed_date is None

        if context['all_good'] == False:
            context['reason_cannot_close'] = mark_safe(
                'Call Evaluation cannot be closed because there are errors.<br>Please fix them and reload the page.')

        context['call_evaluation_is_closed'] = call.callevaluation.closed_date is not None

        if context['all_good']:
            context['show_summary'] = True
        context.update(CallEvaluationSummary.get_call_summary(call))

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'Evaluation validation ({call.little_name()})'}]

        context[CloseCallEvaluation.name] = CloseCallEvaluation(call_id=call.id)

        return context


class CallCloseEvaluation(TemplateView):
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])
        call_evaluation = CallEvaluation.objects.get(call=call)

        context['call'] = call

        projects_created = call_evaluation.close(request.user)

        context['projects_created_count'] = len(projects_created)
        context['projects_created'] = projects_created

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'Call Evaluation ({call.little_name()})',
                                  'url': reverse('logged-call-evaluation-summary', kwargs={'call_id': call.id})},
                                 {'name': f'Close call ({call.little_name()})'}]

        return render(request, 'evaluation/call_evaluation-close-detail.tmpl', context)
