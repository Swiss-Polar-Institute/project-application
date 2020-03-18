from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models.fields.files import FieldFile
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, ListView, DetailView

from ProjectApplication import settings
from comments import utils
from comments.utils import add_comment_attachment_forms, process_comment_attachment
from evaluation.forms.call_evaluation import CallEvaluationForm
from evaluation.forms.close_call_evaluation import CloseCallEvaluation
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.forms.proposal_evaluation import ProposalEvaluationForm
from evaluation.models import CallEvaluation, ProposalEvaluation
from project_core.models import Proposal, Call, ProposalStatus, Project
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

        proposal_evaluation_id = kwargs['pk']
        proposal_evaluation = ProposalEvaluation.objects.get(id=proposal_evaluation_id)

        context = self.prepare_context(request, *args, **{'pk': proposal_evaluation.proposal.id})
        add_proposal_evaluation_form(context, proposal_evaluation.proposal)

        add_comment_attachment_forms(context, 'logged-proposal-evaluation-comment-add', proposal_evaluation)

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

        return render(request, 'evaluation/call_evaluation-list.tmpl', context)


class ProposalEvaluationUpdate(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        if not user_is_in_group_name(request.user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        if 'pk' in kwargs:
            proposal_evaluation = ProposalEvaluation.objects.get(id=kwargs['pk'])
            proposal = proposal_evaluation.proposal
        elif 'proposal' in request.GET:
            proposal_id = request.GET['proposal']
            proposal = Proposal.objects.get(id=proposal_id)
        else:
            assert False

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
            raise PermissionDenied()

        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(id=kwargs['pk'])

        proposal_evaluation_form = ProposalEvaluationForm(request.POST, request.FILES,
                                                          prefix=ProposalEvaluationForm.FORM_NAME,
                                                          proposal=proposal)

        if proposal_evaluation_form.is_valid():
            proposal_evaluation = proposal_evaluation_form.save(user=request.user)

            messages.success(request, 'Evaluation saved')
            return redirect(reverse('logged-proposal-evaluation-detail', kwargs={'pk': proposal_evaluation.id}))
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

            messages.error(request, 'Call evaluation not saved. Verify errors in the form')
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

        add_comment_attachment_forms(context, 'logged-call-evaluation-comment-add', call_evaluation)

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


class ProposalDetail(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(id=kwargs['pk'])

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

        context['can_edit_eligibility'] = proposal.can_eligibility_be_edited()
        context['eligibility_history'] = get_eligibility_history(proposal)

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
            messages.error(request, 'Eligibility not saved. Verify errors in the form')
            context[EligibilityDecisionForm.FORM_NAME] = eligibility_decision_form

            context.update({'active_section': 'evaluation',
                            'active_subsection': 'evaluation-list',
                            'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

            return render(request, 'logged/proposal-detail.tmpl', context)


class CallEvaluationSummary(TemplateView):
    @staticmethod
    def get_call_summary(call):
        summary = {}
        proposals = Proposal.objects.filter(call=call)

        summary['total_number_of_proposals'] = proposals.count()
        summary['total_number_of_eligible'] = proposals.filter(eligibility=Proposal.ELIGIBLE).count()
        summary['total_number_of_funded'] = proposals.filter(
            proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_FUND).count()
        summary['total_number_of_eligible_not_funded'] = summary['total_number_of_eligible'] - summary[
            'total_number_of_funded']

        return summary

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])

        context['call'] = call

        context.update(CallEvaluationSummary.get_call_summary(call))

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'Evaluation summary ({call.little_name()})'}]

        return render(request, 'evaluation/call_evaluation-summary-detail.tmpl', context)


class CallEvaluationValidation(TemplateView):
    @staticmethod
    def _check_call_evaluation_is_completed(call_evaluation):
        required_fields = CallEvaluationForm(call=call_evaluation.call).fields
        missing_fields = []

        for required_field in required_fields:
            value = getattr(call_evaluation, required_field)

            if (type(value) == FieldFile and bool(value) is False) or (value is None):
                missing_fields.append(required_fields[required_field].label)

        edit_link = reverse('logged-call-evaluation-update', kwargs={'pk': call_evaluation.pk})
        return {
            'message_all_good': 'Call Evaluation has been completed',
            'message_problem': mark_safe(
                f'Missing fields in the call evaluation: <em>{",".join(missing_fields)}</em>. <a href="{edit_link}">Edit Call Evaluation</a>'),
            'ok': len(missing_fields) == 0
        }

    @staticmethod
    def _check_all_submitted_proposals_have_eligibility_set(proposals):
        proposals_without_eligibility_set = proposals.filter(
            proposal_status__name=settings.PROPOSAL_STATUS_SUBMITTED).filter(eligibility=Proposal.ELIGIBILITYNOTCHECKED)

        return {'message_problem': 'Not all submitted proposals have had their eligibility checked',
                'message_all_good': 'All submitted proposals have had their eligibility checked',
                'proposals': proposals_without_eligibility_set}

    @staticmethod
    def _check_eligible_proposals_have_evaluation(proposals):
        proposals_without_evaluation = proposals.filter(eligibility=Proposal.ELIGIBLE).filter(
            proposalevaluation=None)

        return {'message_problem': 'There are eligible proposals that have not been evaluated',
                'message_all_good': 'All the eligible proposals have been evaluated',
                'proposals': proposals_without_evaluation}

    @staticmethod
    def _all_good(checks):
        all_good = True
        for check in checks:
            if 'proposals' in check:
                all_good = all_good and check['proposals'].count() == 0
            elif 'ok' in check:
                all_good = all_good and check['ok']
            else:
                assert False

        return all_good

    @staticmethod
    def _check_proposal_evaluations_have_letter_for_applicant(proposals):
        proposals_without_decision_letter = proposals.filter(eligibility=Proposal.ELIGIBLE).filter(
            proposalevaluation__decision_letter='')

        return {'message_problem': 'There are proposals without decision letter',
                'message_all_good': 'All the proposals have a decision letter',
                'proposals': proposals_without_decision_letter}

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])

        proposals = Proposal.objects.filter(call=call)

        proposal_checks = []
        proposal_checks.append(self._check_all_submitted_proposals_have_eligibility_set(proposals))
        proposal_checks.append(self._check_eligible_proposals_have_evaluation(proposals))
        proposal_checks.append(self._check_proposal_evaluations_have_letter_for_applicant(proposals))

        other_checks = []
        other_checks.append(self._check_call_evaluation_is_completed(call.callevaluation))

        context['proposal_checks'] = proposal_checks
        context['other_checks'] = other_checks

        context['call'] = call

        context['all_good'] = CallEvaluationValidation._all_good(proposal_checks + other_checks)
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
                                 {'name': f'Evaluation summary ({call.little_name()})'}]

        context[CloseCallEvaluation.name] = CloseCallEvaluation(call_id=call.id)

        return render(request, 'evaluation/call_evaluation-validation-detail.tmpl', context)


def close_evaluation_call(call, user_closing_call):
    """ It creates the projects and closes the call. """
    created_projects = 0

    with transaction.atomic():
        for proposal in Proposal.objects.filter(call=call).filter(eligibility=Proposal.ELIGIBLE).filter(
                proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_FUND):
            project = Project()

            project.title = proposal.title
            project.location = proposal.location
            project.start_date = proposal.start_date
            project.end_date = proposal.end_date
            project.duration_months = proposal.duration_months
            project.principal_investigator = proposal.applicant

            project.overarching_project = proposal.overarching_project
            project.allocated_budget = proposal.proposalevaluation.allocated_budget
            project.status = Project.ONGOING

            project.call = proposal.call
            project.proposal = proposal

            project.save()
            project.geographical_areas.add(*proposal.geographical_areas.all())
            project.keywords.add(*proposal.keywords.all())

            created_projects += 1

        call_evaluation = CallEvaluation.objects.get(call=call)
        call_evaluation.closed_date = timezone.now()
        call_evaluation.closed_user = user_closing_call
        call_evaluation.save()

    return created_projects


class CallCloseEvaluation(TemplateView):
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['call_id'])

        context['call'] = call

        projects_created = close_evaluation_call(call, request.user)

        context['projects_created_count'] = projects_created

        context.update({'active_section': 'evaluation',
                        'active_subsection': 'evaluation-list',
                        'sidebar_template': 'evaluation/_sidebar-evaluation.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls to evaluate', 'url': reverse('logged-evaluation-list')},
                                 {'name': f'Evaluation summary ({call.little_name()})',
                                  'url': reverse('logged-call-evaluation-summary', kwargs={'call_id': call.id})},
                                 {'name': f'Close call ({call.little_name()})'}]

        return render(request, 'evaluation/call_evaluation-close-detail.tmpl', context)
