import io

import xlsxwriter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, View

from project_core.forms.contacts import ContactForm
from project_core.models import BudgetCategory, PersonPosition
from project_core.views.proposal import AbstractProposalDetailView, AbstractProposalView
from ..forms.call import CallForm, CallQuestionItemFormSet
from ..models import Call
from ..models import Proposal, TemplateQuestion
from django.utils import timezone

CALL_FORM_NAME = 'call_form'
CALL_QUESTION_FORM_NAME = 'call_question_form'
QUESTION_FORM_NAME = 'question_form'


class ContactMixin:
    fields = ['person__first_name', 'person__surname']

    @property
    def success_msg(self):
        return NotImplemented


class ProposalsList(TemplateView):
    template_name = 'management/proposal-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        call_id = self.request.GET.get('call', None)

        context['proposals'] = Proposal.objects.all()
        context['call_filter'] = None

        if call_id is not None:
            context['proposals'] = context['proposals'].filter(call_id=call_id)
            context['call_filter'] = Call.objects.get(id=call_id)

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


class AddCrispySubmitButtonMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

        return form


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


class ContactsListView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contacts'] = PersonPosition.objects.all()

        context['active_section'] = 'contacts'
        context['active_subsection'] = 'contacts-list'
        context['sidebar_template'] = 'management/_sidebar-contacts.tmpl'

        return render(request, 'management/contact-list.tmpl', context)


class ContactUpdateView(UpdateView):
    template_name = 'management/contact-form.tmpl'
    model = PersonPosition
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'contacts'
        context['active_subsection'] = 'contacts-list'
        context['sidebar_template'] = 'management/_sidebar-contacts.tmpl'

        return context

    def get_success_url(self, **kwargs):
        return reverse('contact-detail', kwargs={'pk': self.object.pk})


class ContactsCreateView(SuccessMessageMixin, CreateView):
    template_name = 'management/contact-form.tmpl'
    model = PersonPosition
    success_message = 'Contact created'
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'contacts'
        context['active_subsection'] = 'contacts-add'
        context['sidebar_template'] = 'management/_sidebar-contacts.tmpl'

        return context

    def get_success_url(self, **kwargs):
        return reverse('contact-detail', kwargs={'pk': self.object.pk})


class ContactDetailView(DetailView):
    template_name = 'management/contact-detail.tmpl'
    model = PersonPosition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'contacts'
        context['active_subsection'] = 'contacts-list'
        context['sidebar_template'] = 'management/_sidebar-contacts.tmpl'

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


class ProposalsExportExcel(View):
    def get(self, request, *args, **kwargs):
        call_id = kwargs.get('call', None)

        proposals = Proposal.objects.all().order_by('title')

        date = timezone.now().strftime('%Y%m%d-%H%M%S')
        if call_id:
            proposals = proposals.filter(call_id=call_id)
            filename = 'proposals-{}-{}.xlsx'.format(Call.objects.get(id=call_id).short_name, date)
        else:
            filename = 'proposals-all-{}.xlsx'.format(date)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        for num, proposal in enumerate(proposals):
            worksheet.write(num, 0, proposal.title)

        workbook.close()

        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'management-proposal-detail'
    form_template = 'management/proposal-form.tmpl'

    action_url_update = 'management-proposal-update'
    action_url_add = 'management-proposal-add'

    success_message = 'Proposal updated'

    extra_context = {'active_section': 'proposals',
                     'active_subsection': 'proposals-list',
                     'sidebar_template': 'management/_sidebar-proposals.tmpl'}
