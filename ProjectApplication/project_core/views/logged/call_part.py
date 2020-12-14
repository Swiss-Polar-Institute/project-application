from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, FormView

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
                                 {'name': f'Details ({call.short_name})', 'url': reverse('logged-call-detail', kwargs={'pk': call.pk})},
                                 {'name': 'List Parts'}
                                 ]

        return context


class CallPartForm(FormView):
    pass


class CallPartDetail(DeleteView):
    pass


class CallPartCreate(CreateView):
    pass


class CallPartUpdate(UpdateView):
    pass
