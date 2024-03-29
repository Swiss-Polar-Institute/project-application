from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import UpdateView, CreateView, DetailView, ListView

from project_core.forms.contacts import ContactForm
from project_core.models import PersonPosition


class PersonPositionListView(ListView):
    template_name = 'logged/contact-list.tmpl'
    context_object_name = 'contacts'
    model = PersonPosition
    queryset = PersonPosition.objects.filter(privacy_policy=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contacts'] = PersonPosition.objects.filter(privacy_policy=True)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contact-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')}, {'name': 'People'}]

        return context


class PersonPositionUpdateView(UpdateView):
    template_name = 'logged/contact-form.tmpl'
    model = PersonPosition
    form_class = ContactForm
    prefix = 'contact_form'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contact-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'People', 'url': reverse('logged-person-position-list')},
                                 {'name': 'Edit Person'}]

        return context

    def get_success_url(self, **kwargs):
        return reverse('logged-person-position-detail', kwargs={'pk': self.object.pk})


class PersonPositionCreateView(SuccessMessageMixin, CreateView):
    template_name = 'logged/contact-form.tmpl'
    model = PersonPosition
    success_message = 'Contact created'
    form_class = ContactForm
    prefix = 'contact_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contacts-add',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'People', 'url': reverse('logged-person-position-list')},
                                 {'name': 'Create'}]

        return context

    def get_success_url(self, **kwargs):
        return reverse('logged-person-position-detail', kwargs={'pk': self.object.pk})


class PersonPositionDetailView(DetailView):
    template_name = 'logged/contact-detail.tmpl'
    context_object_name = 'person'
    model = PersonPosition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'contact-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'People', 'url': reverse('logged-person-position-list')},
                                 {'name': 'Details'}]

        return context


class PersonPositionMixin:
    fields = ['person__first_name', 'person__surname']

    @property
    def success_msg(self):
        return NotImplemented
