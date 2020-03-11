from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView, DetailView

from project_core.forms.contacts import ContactForm
from project_core.models import PersonPosition


class PersonPositionListView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contacts'] = PersonPosition.objects.filter(privacy_policy=True)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contact-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')}, {'name': 'People'}]
        return render(request, 'logged/contact-list.tmpl', context)


class PersonPositionUpdateView(UpdateView):
    template_name = 'logged/contact-form.tmpl'
    model = PersonPosition
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contact-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'People', 'url': reverse('person-position-list')},
                                 {'name': 'Edit Person'}]

        return context

    def get_success_url(self, **kwargs):
        return reverse('person-position-detail', kwargs={'pk': self.object.pk})


class PersonPositionCreateView(SuccessMessageMixin, CreateView):
    template_name = 'logged/contact-form.tmpl'
    model = PersonPosition
    success_message = 'Contact created'
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contacts-add',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')}, {'name': 'People'},
                                 {'name': 'Create'}]

        return context

    def get_success_url(self, **kwargs):
        return reverse('person-position-detail', kwargs={'pk': self.object.pk})


class PersonPositionDetailView(DetailView):
    template_name = 'logged/contact-detail.tmpl'
    model = PersonPosition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contact-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'People', 'url': reverse('person-position-list')},
                                 {'name': 'Contact'}]

        return context


class PersonPositionMixin:
    fields = ['person__first_name', 'person__surname']

    @property
    def success_msg(self):
        return NotImplemented
