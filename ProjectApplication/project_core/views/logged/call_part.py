from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from project_core.forms.call_part import CallPartForm
from project_core.models import CallPart, Call


def call_part_section(call):
    return reverse('logged-call-detail', kwargs={'pk': call.pk}) + '#parts'


class CallPartList(ListView):
    model = CallPart
    template_name = 'logged/call_part-list.tmpl'

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
                                  'url': call_part_section(call)},
                                 {'name': 'List Parts'}
                                 ]

        return context


class CallPartDetail(DeleteView):
    template_name = 'logged/call_part-detail.tmpl'
    model = CallPart
    pk_url_kwarg = 'call_part_pk'

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
                                  'url': call_part_section(call)},
                                 {'name': 'List Parts',
                                  'url': reverse('logged-call-part-list', kwargs={'call_pk': call.pk})},
                                 {'name': f'Call Part ({self.object.title_rendered()})'}
                                 ]

        return context


class CallPartCreate(CreateView):
    form_class = CallPartForm
    template_name = 'logged/call_part-form.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(pk=self.kwargs['call_pk'])

        context['call'] = call

        context['action'] = 'Create'

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({call.short_name})',
                                  'url': call_part_section(call)
                                  },
                                 {'name': 'List Parts',
                                  'url': reverse('logged-call-part-list', kwargs={'call_pk': call.pk})},
                                 {'name': f'New Call Part'}
                                 ]

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        form_kwargs['call_pk'] = self.kwargs['call_pk']

        return form_kwargs

    def get_success_url(self):
        return reverse('logged-call-part-detail', kwargs={'call_pk': self.kwargs['call_pk'],
                                                          'call_part_pk': self.object.pk})


class CallPartUpdate(UpdateView):
    model = CallPart
    form_class = CallPartForm
    template_name = 'logged/call_part-form.tmpl'
    pk_url_kwarg = 'call_part_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call = Call.objects.get(pk=self.kwargs['call_pk'])

        context['call'] = call

        context['action'] = 'Edit'

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-call-list')},
                                 {'name': f'Details ({call.short_name})',
                                  'url': call_part_section(call)},
                                 {'name': 'List Parts',
                                  'url': reverse('logged-call-part-list', kwargs={'call_pk': call.pk})},
                                 {'name': f'Call Part ({self.object.title_rendered()})'}
                                 ]

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        form_kwargs['call_pk'] = self.kwargs['call_pk']

        return form_kwargs

    def get_success_url(self):
        return reverse('logged-call-part-detail', kwargs={'call_pk': self.kwargs['call_pk'],
                                                          'call_part_pk': self.kwargs['call_part_pk']})


class CallPartDelete(View):
    def post(self, request, *args, **kwargs):
        call_part_id = request.POST['callPartId']
        call_id = request.POST['callId']

        destination = reverse('logged-call-part-list',
                              kwargs={'call_pk': call_id})

        try:
            call_part = CallPart.objects.get(pk=call_part_id)
        except ObjectDoesNotExist:
            messages.warning(request, 'File could not be found: it has not been deleted')
            return redirect(destination)

        try:
            call_part.delete()
            messages.success(request, 'Call part deleted')
        except ProtectedError:
            messages.error(request,
                           mark_safe(f'Call part "<strong>{call_part.title}</strong>" could not be deleted. Please delete any questions and files attached to the part and try again'))

        return redirect(destination)
