from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from ..models import Proposal, TemplateQuestion
from django.shortcuts import render, redirect
from ..forms.call import CallForm, CallQuestionItemFormSet
from ..forms.question import QuestionForm
from ..models import Call

CALL_FORM_NAME = 'call_form'
CALL_QUESTION_FORM_NAME = 'call_question_form'
QUESTION_FORM_NAME = 'question_form'


class ProposalsList(TemplateView):
    template_name = 'internal/proposal-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['proposals'] = Proposal.objects.all()

        return context


class CallUpdated(TemplateView):
    template_name = 'internal/call-updated.tmpl'

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

        return render(request, 'internal/homepage.tmpl', context)


class CallsList(TemplateView):
    template_name = 'internal/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class QuestionUpdated(TemplateView):
    template_name = 'internal/question-updated.tmpl'

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


class QuestionsList(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['questions'] = TemplateQuestion.objects.all()

        return render(request, 'internal/question-list.tmpl', context)


class QuestionView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            question = TemplateQuestion.objects.get(id=kwargs['id'])
            context[QUESTION_FORM_NAME] = QuestionForm(instance=question, prefix=QUESTION_FORM_NAME)
        else:
            context[QUESTION_FORM_NAME] = QuestionForm(prefix=QUESTION_FORM_NAME)

        return render(request, 'internal/question.tmpl', context)

    def post(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            # Editing an existing question
            question = TemplateQuestion.objects.get(id=kwargs['id'])
            question_form = QuestionForm(request.POST, instance=question, prefix=QUESTION_FORM_NAME)

            context[QUESTION_FORM_NAME] = question_form
            context['question_action_url'] = reverse('question-update', kwargs={'id': question.id})
            action = 'updated'

        else:
            question_form = QuestionForm(request.POST, prefix=QUESTION_FORM_NAME)
            context['question_action_url'] = reverse('question-add')
            action = 'created'

        if question_form.is_valid():
            question = question_form.save()

            return redirect(reverse('question-updated', kwargs={'id': question.id}) + '?action={}'.format(action))

        context = {}

        context[QUESTION_FORM_NAME] = question_form

        return render(request, 'internal/question.tmpl', context)


class CallView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            call_id = kwargs['id']
            call = Call.objects.get(id=call_id)

            context[CALL_FORM_NAME] = CallForm(instance=call, prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(instance=call, prefix=CALL_QUESTION_FORM_NAME)
        else:
            context[CALL_FORM_NAME] = CallForm(prefix=CALL_FORM_NAME)
            context[CALL_QUESTION_FORM_NAME] = CallQuestionItemFormSet(prefix=CALL_QUESTION_FORM_NAME)

        return render(request, 'internal/call.tmpl', context)

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

            return redirect(reverse('internal-call-updated', kwargs={'id': call.id}) + '?action={}'.format(action))

        context = {}

        context[CALL_FORM_NAME] = call_form
        context[CALL_QUESTION_FORM_NAME] = call_question_form

        return render(request, 'internal/call.tmpl', context)
