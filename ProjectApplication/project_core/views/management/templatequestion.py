from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView

from project_core.models import TemplateQuestion


class TemplateQuestionList(TemplateView):
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