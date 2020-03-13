from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from ProjectApplication import settings
from comments import utils
from comments.utils import add_comment_attachment_forms, process_comment_attachment
from evaluation.forms.call_evaluation import CallEvaluationForm
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.forms.proposal_evaluation import ProposalEvaluationForm
from evaluation.models import CallEvaluation, ProposalEvaluation
from project_core.models import Proposal, Call, ProposalStatus
from project_core.utils import user_is_in_group_name
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

        proposal_evaluation_id = kwargs['id']
        proposal_evaluation = ProposalEvaluation.objects.get(id=proposal_evaluation_id)

        context = self.prepare_context(request, *args, **{'id': proposal_evaluation.proposal.id})
        add_proposal_evaluation_form(context, proposal_evaluation.proposal)

        add_comment_attachment_forms(context, 'logged-proposal-evaluation-comment-add', proposal_evaluation)

        board_decision = proposal_evaluation.board_decision

        if board_decision == ProposalEvaluation.BOARD_DECISION_FUND:
            board_decision_badge_class = 'badge-success'
        elif board_decision == ProposalEvaluation.BOARD_DECISION_DO_NOT_FUND:
            board_decision_badge_class = 'badge-danger'
        else:
            assert False

        panel_recommendation = proposal_evaluation.panel_recommendation

        if panel_recommendation == ProposalEvaluation.PANEL_RECOMMENDATION_FUND:
            panel_recommendation_badge_class = 'badge-success'
        elif panel_recommendation == ProposalEvaluation.PANEL_RECOMMENDATION_RESERVE:
            panel_recommendation_badge_class = 'badge-warning'
        elif panel_recommendation == ProposalEvaluation.PANEL_RECOMMENDATION_DO_NOT_FUND:
            panel_recommendation_badge_class = 'badge-danger'
        else:
            assert False

        context['board_decision_badge_class'] = board_decision_badge_class
        context['panel_recommendation_badge_class'] = panel_recommendation_badge_class

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
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.closed_calls()

        context['proposals_no_draft_only'] = True

        context.update({'view_button': False,
                        'edit_button': False,
                        'proposal_call_list_button': False,
                        'proposal_evaluation_list_button': True,
                        'evaluation_spreadsheet_button': True,
                        'view_evaluation_button': True,
                        'evaluation_close_button': True
                        })

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls to evaluate'}]

        return render(request, 'evaluation/evaluation-list.tmpl', context)


class ProposalEvaluationUpdate(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        if 'id' in kwargs:
            proposal_evaluation = ProposalEvaluation.objects.get(id=kwargs['id'])
            proposal = proposal_evaluation.proposal
        elif 'proposal' in request.GET:
            proposal_id = request.GET['proposal']
            proposal = Proposal.objects.get(id=proposal_id)
        else:
            assert False

        context = self.prepare_context(request, *args, **{'id': proposal.id})

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
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(id=kwargs['id'])

        proposal_evaluation_form = ProposalEvaluationForm(request.POST, request.FILES,
                                                          prefix=ProposalEvaluationForm.FORM_NAME,
                                                          proposal=proposal)

        if proposal_evaluation_form.is_valid():
            proposal_evaluation = proposal_evaluation_form.save(user=request.user)

            messages.success(request, 'Evaluation saved')
            return redirect(reverse('logged-proposal-evaluation-detail', kwargs={'id': proposal_evaluation.id}))
        else:
            messages.error(request, 'Evaluation not saved. Verify errors in the form')
            context[ProposalEvaluationForm.FORM_NAME] = proposal_evaluation_form

            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            return render(request, 'logged/proposal-detail-evaluation-form.tmpl', context)


class CallEvaluationUpdate(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'id' in kwargs:
            call_evaluation = CallEvaluation.objects.get(id=kwargs['id'])
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

        if 'id' in kwargs:
            call_evaluation = CallEvaluation.objects.get(id=kwargs['id'])
            call = call_evaluation.call
        else:
            call_evaluation = None
            call = Call.objects.get(id=self.request.GET['call'])

        call_evaluation_form = CallEvaluationForm(request.POST, request.FILES, instance=call_evaluation,
                                                  prefix=CallEvaluationForm.FORM_NAME, call=call)

        if call_evaluation_form.is_valid():
            call_evaluation = call_evaluation_form.save_call_evaluation(user=request.user)

            messages.success(request, 'Call evaluation saved')
            return redirect(reverse('logged-call-evaluation-detail', kwargs={'id': call_evaluation.id}))
        else:
            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            messages.alert(request, 'Call evaluation not saved. Verify errors in the form')
            context[CallEvaluationForm.FORM_NAME] = call_evaluation_form

            context['call'] = call

            return render(request, 'evaluation/call_evaluation-form.tmpl', context)


class ProposalList(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])
        draft = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_DRAFT)
        proposals = Proposal.objects.filter(call=call).exclude(proposal_status=draft)

        context['call'] = call
        context['proposals'] = proposals

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'List of proposals ({call.little_name()})'}]

        return render(request, 'evaluation/evaluation_list-proposals.tmpl', context)


class CallEvaluationDetail(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': 'View call evaluation'}]

        call_evaluation = CallEvaluation.objects.get(id=kwargs['id'])
        context['call_evaluation'] = call_evaluation

        add_comment_attachment_forms(context, 'logged-call-evaluation-comment-add', call_evaluation)

        return render(request, 'evaluation/call_evaluation-detail.tmpl', context)


class CallEvaluationCommentAdd(TemplateView):
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        call_evaluation = CallEvaluation.objects.get(id=kwargs['id'])

        result = process_comment_attachment(request, context, 'logged-call-evaluation-detail',
                                            'logged-proposal-call-comment-add',
                                            'logged/call-evaluation-detail.tmpl',
                                            call_evaluation)

        return result


class ProposalDetail(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(id=kwargs['id'])

        utils.add_comment_attachment_forms(context, 'logged-call-evaluation-proposal-detail', proposal)

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

        return render(request, 'evaluation/proposal-detail.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        proposal = Proposal.objects.get(id=kwargs['id'])

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

        proposal_evaluation = ProposalEvaluation.objects.get(id=kwargs['id'])

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

        proposal_id = kwargs['id']

        eligibility_decision_form = EligibilityDecisionForm(request.POST, prefix=EligibilityDecisionForm.FORM_NAME,
                                                            proposal_id=proposal_id)

        if eligibility_decision_form.is_valid():
            eligibility_decision_form.save_eligibility(request.user)

            messages.success(request, 'Eligibility saved')
            return redirect(reverse('logged-call-evaluation-proposal-detail', kwargs={'id': proposal_id}))

        else:
            messages.alert(request, 'Eligibility not saved. Verify errors in the form')
            context[EligibilityDecisionForm.FORM_NAME] = eligibility_decision_form

            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            return render(request, 'logged/proposal-detail.tmpl', context)


class CloseEvaluation(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])

        context['call'] = call

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        proposals = Proposal.objects.filter(call=call)

        checks = []

        eligible_proposals_without_evaluation = proposals.filter(eligibility=Proposal.ELIGIBLE).filter(
            proposalevaluation=None)

        checks.append({'message_problem': 'There are eligible proposals without an evaluation',
                       'message_all_good': 'All the eligible proposals have an evaluation',
                       'proposals': eligible_proposals_without_evaluation})

        not_funded_without_letter_for_applicant = proposals.filter(
            proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_DO_NOT_FUND).filter(
            Q(proposalevaluation__feedback_to_applicant='') | Q(proposalevaluation__feedback_to_applicant__isnull=True))

        checks.append(
            {'message_problem': 'There are proposals that are not funded and don\'t have a letter for the applicant',
             'message_all_good': 'All the not funded proposals have a letter for the applicant',
             'proposals': not_funded_without_letter_for_applicant})

        context['checks'] = checks
        context['all_good'] = CloseEvaluation._all_good(checks)

        if context['all_good']:
            context['total_number_of_proposals'] = proposals.count()
            context['total_number_of_eligible'] = proposals.filter(eligibility=Proposal.ELIGIBLE).count()
            context['total_number_of_funded'] = proposals.filter(
                proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_FUND).count()
            context['total_number_of_eligible_not_funded'] = context['total_number_of_eligible'] - context[
                'total_number_of_funded']

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'Close evaluation ({call.little_name()})'}]

        return render(request, 'evaluation/close-evaluation.tmpl', context)

    @staticmethod
    def _all_good(proposals):
        all_good = True
        for proposal in proposals:
            all_good = all_good and proposal['proposals'].count() == 0

        return all_good
