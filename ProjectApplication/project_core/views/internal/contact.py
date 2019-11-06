from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView, DetailView

from project_core.forms.contacts import ContactForm
from project_core.models import PersonPosition


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