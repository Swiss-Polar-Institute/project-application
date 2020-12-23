from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView, FormView

from project_core.call_question import CallQuestionForm, CallQuestionFromTemplateQuestionForm
from project_core.models import CallQuestion


class CallQuestionView(TemplateView):
    template_name = 'logged/question_answer-detail.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call_question = CallQuestion.objects.get(pk=self.kwargs['call_question_pk'])

        context['call_question'] = call_question

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        url_call_parts_anchor = reverse('logged-call-detail', kwargs={'pk': call_question.call_part.call.pk}) + '#parts'

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'Details ({call_question.call_part.call.little_name()})',
                                  'url': url_call_parts_anchor},
                                 {'name': call_question.question_text}
                                 ]

        return context


class CallQuestionUpdate(SuccessMessageMixin, UpdateView):
    model = CallQuestion
    template_name = 'logged/question_answer-form.tmpl'
    form_class = CallQuestionForm
    pk_url_kwarg = 'call_question_pk'
    context_object_name = 'call_question'
    success_message = 'Call question updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call_question = context['call_question']

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        call = call_question.call_part.call

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'Details ({call.little_name()})',
                                  'url': reverse('logged-call-update', kwargs={'pk': call.pk})+'#parts'},
                                 {'name': call_question.question_text}
                                 ]

        return context

    def get_success_url(self):
        return reverse('logged-call-question-detail', kwargs={'call_pk': self.object.call_part.call.pk,
                                                              'call_question_pk': self.object.pk
                                                              })


class CallQuestionTemplateQuestionUpdate(SuccessMessageMixin, FormView):
    template_name = 'logged/question_answer-form.tmpl'
    form_class = CallQuestionFromTemplateQuestionForm
    success_message = 'Question(s) added'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'TODO2'}]

        return context

    def form_valid(self, form):
        is_valid_form = super().form_valid(form)
        if is_valid_form:
            form.save()

        return is_valid_form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['call_part_pk'] = self.kwargs['call_part_pk']
        return kwargs

    def get_success_url(self):
        call_pk = self.kwargs['call_pk']

        return reverse('logged-call-update', kwargs={'pk': call_pk}) + '#parts'


class CallQuestionCreate(SuccessMessageMixin, CreateView):
    model = CallQuestion
    template_name = 'logged/question_answer-form.tmpl'
    form_class = CallQuestionForm
    context_object_name = 'call_question'
    success_message = 'Call question added'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'TODO2'}]

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['call_part_pk'] = self.kwargs['call_part_pk']
        return kwargs

    def get_success_url(self):
        return reverse('logged-call-question-detail', kwargs={'call_pk': self.object.call_part.call.pk,
                                                              'call_question_pk': self.object.pk
                                                              }) + '#parts'
