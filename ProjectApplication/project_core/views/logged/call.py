from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from comments.forms.attachment import AttachmentForm
from comments.models import CallAttachmentCategory, CallCommentCategory
from comments.utils import process_comment_attachment, adds_comment_attachment_forms
from project_core.forms.call import CallForm, CallQuestionItemFormSet
from project_core.models import Call, BudgetCategory
from variable_templates.forms.template_variables import TemplateVariableItemFormSet
from variable_templates.utils import copy_template_variables_from_funding_instrument_to_call, \
    get_template_variables_for_call
from .funding_instrument import TEMPLATE_VARIABLES_FORM_NAME

CALL_QUESTION_FORM_NAME = 'call_question_form'
CALL_FORM_NAME = 'call_form'


class CallsList(TemplateView):
    template_name = 'logged/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['open_calls'] = Call.open_calls()
        context['closed_calls'] = Call.closed_calls()
        context['future_calls'] = Call.future_calls()

        context['active_section'] = 'calls'
        context['active_subsection'] = 'calls-list'
        context['sidebar_template'] = 'logged/_sidebar-calls.tmpl'

        return context


class AbstractCallView(TemplateView):
    def prepare_context(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['id'])

        context['call'] = call
        context['active_section'] = 'calls'
        context['active_subsection'] = 'calls-list'
        context['sidebar_template'] = 'logged/_sidebar-calls.tmpl'
        context['template_variables'] = get_template_variables_for_call(call)

        call_budget_categories_names = list(call.budget_categories.all().values_list('name', flat=True))

        budget_categories_status = []

        for budget_category_name in BudgetCategory.all_ordered().values_list('name', flat=True):
            in_call = budget_category_name in call_budget_categories_names
            budget_categories_status.append({'in_call': in_call,
                                             'name': budget_category_name})

        context['budget_categories_status'] = budget_categories_status

        adds_comment_attachment_forms(context, 'logged-call-comment-add', call)

        return context


class CallDetailView(AbstractCallView):
    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        return render(request, 'logged/call-detail.tmpl', context)


class CallCommentAdd(AbstractCallView):
    def post(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'calls-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        call = Call.objects.get(id=kwargs['id'])

        result = process_comment_attachment(request, context, 'logged-call-detail',
                                            'logged-call-comment-add',
                                            'logged/call-detail.tmpl',
                                            call)

        return result


class CallView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'id' in kwargs:
            call_id = kwargs['id']
            call = Call.objects.get(id=call_id)

            context[CALL_FORM_NAME] = CallForm(instance=call, prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(instance=call, prefix=CALL_QUESTION_FORM_NAME)
            context[TEMPLATE_VARIABLES_FORM_NAME] = TemplateVariableItemFormSet(call=call,
                                                                                prefix=TEMPLATE_VARIABLES_FORM_NAME)
            context['call_action_url'] = reverse('logged-call-update', kwargs={'id': call_id})
            context['call_action'] = 'Edit'
            context['active_subsection'] = 'calls-list'

        else:
            context[CALL_FORM_NAME] = CallForm(prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(prefix=CALL_QUESTION_FORM_NAME)
            context[TEMPLATE_VARIABLES_FORM_NAME] = TemplateVariableItemFormSet(prefix=TEMPLATE_VARIABLES_FORM_NAME)
            context['call_action_url'] = reverse('call-add')
            context['call_action'] = 'Create'
            context['active_subsection'] = 'call-add'

        context['active_section'] = 'calls'
        context['sidebar_template'] = 'logged/_sidebar-calls.tmpl'

        return render(request, 'logged/call.tmpl', context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        new_call = False
        template_variables_form = None  # avoids warning referenced without initialization

        if 'id' in kwargs:
            call = Call.objects.get(id=kwargs['id'])
            call_form = CallForm(request.POST, instance=call, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, instance=call, prefix=CALL_QUESTION_FORM_NAME)
            template_variables_form = TemplateVariableItemFormSet(request.POST, call=call,
                                                                  prefix=TEMPLATE_VARIABLES_FORM_NAME)

            context['call_action_url'] = reverse('logged-call-update', kwargs={'id': call.id})
            call_action = 'Edit'
            action = 'updated'
            active_subsection = 'calls-list'

            to_validate = [call_form, call_question_form, template_variables_form]

        else:
            # creates a call
            new_call = True
            call_form = CallForm(request.POST, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, prefix=CALL_QUESTION_FORM_NAME)

            context['call_action_url'] = reverse('call-add')
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
            return redirect(reverse('logged-call-detail', kwargs={'id': call.id}) + '?action={}'.format(action))

        context = super().get_context_data(**kwargs)

        context['call_action'] = call_action
        context[CALL_FORM_NAME] = call_form
        context[CALL_QUESTION_FORM_NAME] = call_question_form
        context[TEMPLATE_VARIABLES_FORM_NAME] = template_variables_form

        context['active_section'] = 'calls'
        context['active_subsection'] = active_subsection
        context['sidebar_template'] = 'logged/_sidebar-calls.tmpl'

        messages.error(request, 'Call not saved. Please correct the errors in the form and try again')

        return render(request, 'logged/call.tmpl', context)
