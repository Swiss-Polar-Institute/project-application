from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView

from project_core.call_question import CallQuestionForm
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
                                 {'name': 'TODO'}
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

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'Details ({call_question.call_part.call.little_name()})',
                                  'url': 'TODO'},
                                 {'name': 'TODO'}
                                 ]

        return context

    def get_success_url(self):
        return reverse('logged-call-question-detail', kwargs={'call_pk': self.object.call_part.call.pk,
                                                              'call_question_pk': self.object.pk
                                                              })

class CallQuestionCreate(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
