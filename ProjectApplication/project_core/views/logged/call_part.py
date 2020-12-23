from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from project_core.forms.call_part import CallPartForm
from project_core.models import CallPart, Call


class CallPartList(ListView):
    model = CallPart
    template_name = 'logged/call-part-list.tmpl'

    def get_queryset(self):
        return CallPart.objects.filter(call_id=self.kwargs['call_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(pk=self.kwargs['call_pk'])

        context['call'] = call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({call.short_name})',
                                  'url': reverse('logged-call-detail', kwargs={'pk': call.pk})},
                                 {'name': 'List Parts'}
                                 ]

        return context


class CallPartDetail(DeleteView):
    template_name = 'logged/call-part-detail.tmpl'
    model = CallPart
    pk_url_kwarg = 'proposal_part_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = self.object.call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['call'] = call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({call.short_name})',
                                  'url': reverse('logged-call-detail', kwargs={'pk': call.pk})},
                                 {'name': f'Call Part ({self.object.title})'}
                                 ]

        return context


class CallPartCreate(CreateView):
    form_class = CallPartForm
    template_name = 'logged/call-part-form.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(pk=self.kwargs['call_pk'])

        context['call'] = call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({call.short_name})',
                                  'url': reverse('logged-call-detail', kwargs={'pk': call.pk})},
                                 {'name': f'New Call Part'}
                                 ]

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        form_kwargs['call_pk'] = self.kwargs['call_pk']

        return form_kwargs

    def get_success_url(self):
        return reverse('logged-call-part-detail', kwargs={'call_pk': self.kwargs['call_pk'],
                                                          'proposal_part_pk': self.object.pk})


class CallPartUpdate(UpdateView):
    model = CallPart
    form_class = CallPartForm
    template_name = 'logged/call-part-form.tmpl'
    pk_url_kwarg = 'proposal_part_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(pk=self.kwargs['call_pk'])

        context['call'] = call

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({call.short_name})',
                                  'url': reverse('logged-call-detail', kwargs={'pk': call.pk})},
                                 {'name': f'Call Part ({self.object.title})'}
                                 ]

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        form_kwargs['call_pk'] = self.kwargs['call_pk']

        return form_kwargs

    def get_success_url(self):
        return reverse('logged-call-part-detail', kwargs={'call_pk': self.kwargs['call_pk'],
                                                          'proposal_part_pk': self.kwargs['proposal_part_pk']})
