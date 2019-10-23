from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView

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

        return context


class CallUpdated(TemplateView):
    template_name = 'management/call-updated.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['id'] = kwargs['id']
        action = self.request.GET['action']

        if action in ('created', 'updated'):
            context['action'] = action
        else:
            # should not happen
            context['action'] = ''

        return context


class Homepage(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        return render(request, 'management/homepage.tmpl', context)


class CallsList(TemplateView):
    template_name = 'management/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['open_calls'] = Call.open_calls()
        context['closed_calls'] = Call.closed_calls()
        context['future_calls'] = Call.future_calls()

        return context


class QuestionsList(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['questions'] = TemplateQuestion.objects.all()

        return render(request, 'management/templatequestion_list.tmpl', context)


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
    template_name = 'management/templatequestion_form.tmpl'
    model = TemplateQuestion
    success_message = 'Question created'


class TemplateQuestionUpdateView(TemplateQuestionMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, UpdateView):
    template_name = 'management/templatequestion_form.tmpl'
    model = TemplateQuestion
    success_message = 'Question updated'


class TemplateQuestionDetailView(TemplateQuestionMixin, DetailView):
    template_name = 'management/templatequestion_detail.tmpl'
    model = TemplateQuestion


class CallView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            call_id = kwargs['id']
            call = Call.objects.get(id=call_id)

            context[CALL_FORM_NAME] = CallForm(instance=call, prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(instance=call, prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('call-update', kwargs={'id': call_id})
        else:
            context[CALL_FORM_NAME] = CallForm(prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('call-add')

        return render(request, 'management/call.tmpl', context)

    def post(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            call = Call.objects.get(id=kwargs['id'])
            call_form = CallForm(request.POST, instance=call, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, instance=call, prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('call-update', kwargs={'id': call.id})
            action = 'updated'

        else:
            # creates a call
            call_form = CallForm(request.POST, prefix=CALL_FORM_NAME)
            call_question_form = CallQuestionItemFormSet(request.POST, prefix=CALL_QUESTION_FORM_NAME)
            context['call_action_url'] = reverse('call-add')
            action = 'created'

        if call_form.is_valid() and call_question_form.is_valid():
            call = call_form.save()
            call_question_form.save()

            return redirect(reverse('management-call-updated', kwargs={'id': call.id}) + '?action={}'.format(action))

        context = {}

        context[CALL_FORM_NAME] = call_form
        context[CALL_QUESTION_FORM_NAME] = call_question_form

        messages.error(request, 'Call not saved. Please correct the errors in the form and try again')

        return render(request, 'management/call.tmpl', context)
