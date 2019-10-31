from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView

from project_core.models import BudgetCategory
from project_core.views.proposal import AbstractProposalDetailView, AbstractProposalView
from ..forms.call import CallForm, CallQuestionItemFormSet
from ..models import Call
from ..models import Proposal, TemplateQuestion

CALL_FORM_NAME = 'call_form'
CALL_QUESTION_FORM_NAME = 'call_question_form'
QUESTION_FORM_NAME = 'question_form'


class ProposalsList(TemplateView):
    template_name = 'management/proposal-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['proposals'] = Proposal.objects.all()

        context['active_section'] = 'proposals'
        context['active_subsection'] = 'proposals-list'
        context['sidebar_template'] = 'management/_sidebar-proposals.tmpl'

        return context


class Homepage(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'home'
        context['active_subsection'] = 'home'
        context['sidebar_template'] = 'management/_sidebar-homepage.tmpl'

        return render(request, 'management/homepage.tmpl', context)


class CallsList(TemplateView):
    template_name = 'management/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['open_calls'] = Call.open_calls()
        context['closed_calls'] = Call.closed_calls()
        context['future_calls'] = Call.future_calls()

        context['active_section'] = 'calls'
        context['active_subsection'] = 'calls-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context


class QuestionsList(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['template_questions'] = TemplateQuestion.objects.all()

        context['active_section'] = 'calls'
        context['active_subsection'] = 'template-questions-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return render(request, 'management/templatequestion-list.tmpl', context)


class TemplateQuestionMixin:
    fields = ['question_text', 'question_description', 'answer_max_length']

    @property
    def success_msg(self):
        return NotImplemented


class AddCrispySubmitButtonMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

        return form


class TemplateQuestionCreateView(TemplateQuestionMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, CreateView):
    template_name = 'management/templatequestion-form.tmpl'
    model = TemplateQuestion
    success_message = 'Template question created'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'template-questions-add'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context


class TemplateQuestionUpdateView(TemplateQuestionMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, UpdateView):
    template_name = 'management/templatequestion-form.tmpl'
    model = TemplateQuestion
    success_message = 'Template question updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'template-questions-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context


class TemplateQuestionDetailView(TemplateQuestionMixin, DetailView):
    template_name = 'management/templatequestion-detail.tmpl'
    model = TemplateQuestion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'template-questions-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context


class CallDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(id=kwargs['id'])

        context['call'] = call
        context['active_section'] = 'calls'
        context['active_subsection'] = 'calls-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        call_budget_categories_names = list(call.budget_categories.all().values_list('name', flat=True))

        budget_categories_status = []

        for budget_category_name in BudgetCategory.all_ordered().values_list('name', flat=True):
            in_call = budget_category_name in call_budget_categories_names
            budget_categories_status.append({'in_call': in_call,
                                             'name': budget_category_name})

        context['budget_categories_status'] = budget_categories_status
        return render(request, 'management/call-detail.tmpl', context)


class CallView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'id' in kwargs:
            call_id = kwargs['id']
            call = Call.objects.get(id=call_id)

            context[CALL_FORM_NAME] = CallForm(instance=call, prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(instance=call, prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('management-call-update', kwargs={'id': call_id})
            context['call_action'] = 'Edit'
            context['active_subsection'] = 'calls-list'

        else:
            context[CALL_FORM_NAME] = CallForm(prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('call-add')
            context['call_action'] = 'Create'
            context['active_subsection'] = 'call-add'

        context['active_section'] = 'calls'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return render(request, 'management/call.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'id' in kwargs:
            call = Call.objects.get(id=kwargs['id'])
            call_form = CallForm(request.POST, instance=call, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, instance=call, prefix=CALL_QUESTION_FORM_NAME)

            context['call_action_url'] = reverse('management-call-update', kwargs={'id': call.id})
            call_action = 'Edit'
            action = 'updated'
            active_subsection = 'calls-list'

        else:
            # creates a call
            call_form = CallForm(request.POST, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('call-add')
            context['call_action'] = 'Create'
            call_action = 'Create'
            action = 'created'
            active_subsection = 'call-add'

        if call_form.is_valid() and call_question_form.is_valid():
            call = call_form.save()
            call_question_form.save()

            messages.success(request, 'Call has been saved')
            return redirect(reverse('management-call-detail', kwargs={'id': call.id}) + '?action={}'.format(action))

        context = super().get_context_data(**kwargs)

        context['call_action'] = call_action
        context[CALL_FORM_NAME] = call_form
        context[CALL_QUESTION_FORM_NAME] = call_question_form

        context['active_section'] = 'calls'
        context['active_subsection'] = active_subsection
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        messages.error(request, 'Call not saved. Please correct the errors in the form and try again')

        return render(request, 'management/call.tmpl', context)


class ProposalDetailView(AbstractProposalDetailView):
    template = 'management/proposal-detail.tmpl'

    extra_context = {'active_section': 'proposals',
                     'active_subsection': 'proposals-list',
                     'sidebar_template': 'management/_sidebar-proposals.tmpl'}


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'management-proposal-detail'
    form_template = 'management/proposal-form.tmpl'

    action_url_update = 'management-proposal-update'
    action_url_add = 'management-proposal-add'

    success_message = 'Proposal updated'

    extra_context = {'active_section': 'proposals',
                     'active_subsection': 'proposals-list',
                     'sidebar_template': 'management/_sidebar-proposals.tmpl'}
