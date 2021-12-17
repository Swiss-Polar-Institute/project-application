from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView

from project_core.forms.financial_key import FinancialKeyForm
from project_core.models import FinancialKey


class FinancialKeyListView(ListView):
    template_name = 'logged/financial_key-list.tmpl'
    context_object_name = 'financial_keys'
    model = FinancialKey

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'financial_key-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Financial keys'}]

        return context


class FinancialKeyAdd(SuccessMessageMixin, CreateView):
    template_name = 'logged/financial_key-form.tmpl'
    model = FinancialKey
    success_message = 'Financial key created'
    form_class = FinancialKeyForm
    success_url = reverse_lazy('logged-financial-key-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'financial_key-add',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Financial keys', 'url': reverse('logged-financial-key-list')},
                                 {'name': 'Create'}]

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)