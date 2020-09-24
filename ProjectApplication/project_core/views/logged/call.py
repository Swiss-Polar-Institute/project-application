from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from ProjectApplication import settings
from comments import utils
from comments.utils import process_comment_attachment, comments_attachments_forms
from project_core.forms.call import CallForm, CallQuestionItemFormSet
from project_core.models import Call, BudgetCategory, Proposal, FundingInstrument
from variable_templates.forms.template_variables import TemplateVariableItemFormSet
from variable_templates.utils import copy_template_variables_from_funding_instrument_to_call, \
    get_template_variables_for_call
from .funding_instrument import TEMPLATE_VARIABLES_FORM_NAME
from ..common.proposal import AbstractProposalDetailView

CALL_QUESTION_FORM_NAME = 'call_question_form'
CALL_FORM_NAME = 'call_form'


class CallList(TemplateView):
    template_name = 'logged/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'view_button': True,
                        'edit_button': True,
                        'proposal_call_list_button': True,
                        'proposal_evaluation_list_button': False,
                        'evaluation_spreadsheet_button': False,
                        'evaluation_summary_or_validation_button': False})

        context.update({'open_calls': Call.open_calls(),
                        'closed_calls': Call.closed_calls(),
                        'future_calls': Call.future_calls()})

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls'}]

        return context


class AbstractCallView(TemplateView):
    def prepare_context(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['pk'])

        context['call'] = call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['template_variables'] = get_template_variables_for_call(call)

        call_budget_categories_names = list(call.budget_categories.all().values_list('name', flat=True))

        budget_categories_status = []

        for budget_category_name in BudgetCategory.all_ordered().values_list('name', flat=True):
            in_call = budget_category_name in call_budget_categories_names
            budget_categories_status.append({'in_call': in_call,
                                             'name': budget_category_name})

        context['budget_categories_status'] = budget_categories_status

        context.update(comments_attachments_forms('logged-call-comment-add', call))

        if call.evaluation_is_closed():
            url = self.request.build_absolute_uri(reverse('lay-summaries-for_website', kwargs={'call': call.id}))
            if settings.HTTP_AUTH_INCOMING_LINKS:
                username_password_tag = f' userpwd="{settings.HTTP_AUTH_INCOMING_LINKS}"'
            else:
                username_password_tag = ''

            context['public_lay_summaries_for_website_url'] = f'[remote_content url="{url}"{username_password_tag}]'

        return context


class CallDetailView(AbstractCallView):
    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({context["call"].short_name})'}]

        return render(request, 'logged/call-detail.tmpl', context)


class CallCommentAdd(AbstractCallView):
    def post(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        call = Call.objects.get(id=kwargs['pk'])

        result = process_comment_attachment(request, context, 'logged-call-detail',
                                            'logged-call-comment-add',
                                            'logged/call-detail.tmpl',
                                            call)

        return result


class ProposalList(ListView):
    template_name = 'logged/_call_list-proposals.tmpl'
    model = Proposal
    context_object_name = 'proposals'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=self.kwargs['call_id'])

        context['call'] = call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'List of proposals ({call.little_name()})'}]

        return context

    def get_queryset(self):
        call = Call.objects.get(id=self.kwargs['call_id'])
        return Proposal.objects.filter(call=call)


class ProposalDetail(AbstractProposalDetailView):
    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        proposal = Proposal.objects.get(id=kwargs['pk'])

        context['external_url'] = self.request.build_absolute_uri(
            reverse('proposal-update', kwargs={'uuid': proposal.uuid}))

        context.update(utils.comments_attachments_forms('logged-call-proposal-detail', proposal))

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'List of proposals ({proposal.call.little_name()})',
                                  'url': reverse('logged-call-list-proposals', kwargs={'call_id': proposal.call.id})},
                                 {'name': 'Proposal'}]

        return render(request, 'logged/proposal-detail.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        proposal = Proposal.objects.get(id=kwargs['pk'])

        result = process_comment_attachment(request, context, 'logged-call-proposal-detail',
                                            'logged-call-comment-add',
                                            'logged/proposal-detail.tmpl',
                                            proposal)

        return result


def get_funding_instruments_data():
    funding_instruments_data = {}

    for funding_instrument in FundingInstrument.objects.all():
        funding_instruments_data[funding_instrument.id] = {'long_name': funding_instrument.long_name,
                                                           'short_name': funding_instrument.short_name.name
                                                           }

    return funding_instruments_data


class CallView(TemplateView):
    template_name = 'logged/call-form.tmpl'

    @staticmethod
    def _cancel_url(kwargs):
        if 'pk' in kwargs:
            return reverse('logged-call-detail', kwargs={'pk': kwargs['pk']})
        else:
            return reverse('logged-call-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = CallView._cancel_url(kwargs)

        if 'pk' in kwargs:
            call_id = kwargs['pk']
            call = Call.objects.get(id=call_id)

            context[CALL_FORM_NAME] = CallForm(instance=call, prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(instance=call, prefix=CALL_QUESTION_FORM_NAME)
            context[TEMPLATE_VARIABLES_FORM_NAME] = TemplateVariableItemFormSet(call=call,
                                                                                prefix=TEMPLATE_VARIABLES_FORM_NAME)
            context['call_action_url'] = reverse('logged-call-update', kwargs={'pk': call_id})
            context['call_action'] = 'Edit'

            context['active_subsection'] = 'call-list'
            breadcrumb_page = f'{context["call_action"]} ({call.little_name()})'

        else:
            context[CALL_FORM_NAME] = CallForm(prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(prefix=CALL_QUESTION_FORM_NAME)
            context[TEMPLATE_VARIABLES_FORM_NAME] = TemplateVariableItemFormSet(prefix=TEMPLATE_VARIABLES_FORM_NAME)
            context['call_action_url'] = reverse('logged-call-add')
            context['call_action'] = 'Create'

            context['active_subsection'] = 'call-add'

            breadcrumb_page = 'Create'

        context['funding_instruments_data'] = get_funding_instruments_data()
        context['active_section'] = 'calls'
        context['sidebar_template'] = 'logged/_sidebar-calls.tmpl'

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': breadcrumb_page}]

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = CallView._cancel_url(kwargs)

        new_call = False
        template_variables_form = None  # avoids warning referenced without initialization

        if 'pk' in kwargs:
            call = Call.objects.get(id=kwargs['pk'])
            call_form = CallForm(request.POST, instance=call, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, instance=call, prefix=CALL_QUESTION_FORM_NAME)
            template_variables_form = TemplateVariableItemFormSet(request.POST, call=call,
                                                                  prefix=TEMPLATE_VARIABLES_FORM_NAME)

            context['call_action_url'] = reverse('logged-call-update', kwargs={'pk': call.id})
            call_action = 'Edit'
            action = 'updated'
            active_subsection = 'call-list'

            to_validate = [call_form, call_question_form, template_variables_form]

        else:
            # creates a call
            new_call = True
            call_form = CallForm(request.POST, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, prefix=CALL_QUESTION_FORM_NAME)

            context['call_action_url'] = reverse('logged-call-add')
            context['call_action'] = 'Create'
            call_action = 'Create'
            action = 'created'
            active_subsection = 'call-add'

            to_validate = [call_form, call_question_form]

        all_valid = True
        for form in to_validate:
            valid_form = form.is_valid()
            all_valid = all_valid and valid_form

        if all_valid:
            call = call_form.save()
            call_question_form.save()

            if new_call:
                copy_template_variables_from_funding_instrument_to_call(call)
            else:
                template_variables_form.save_into_call(call)

            messages.success(request, 'Call has been saved')
            return redirect(reverse('logged-call-detail', kwargs={'pk': call.id}) + '?action={}'.format(action))

        context = super().get_context_data(**kwargs)

        context['call_action'] = call_action
        context[CALL_FORM_NAME] = call_form
        context[CALL_QUESTION_FORM_NAME] = call_question_form
        context[TEMPLATE_VARIABLES_FORM_NAME] = template_variables_form

        context.update({'active_section': 'calls',
                        'active_subsection': active_subsection,
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        messages.error(request, 'Call not saved. Please correct the errors in the form and try again.')

        return render(request, 'logged/call-form.tmpl', context)
