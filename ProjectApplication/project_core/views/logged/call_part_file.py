from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView, ListView

from project_core.forms.call_part_file import CallPartFileForm
from project_core.models import Call, CallPart, CallPartFile


class CallPartFileList(ListView):
    template_name = 'logged/call_part_file-list.tmpl'
    model = CallPartFile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['callpart'] = CallPart.objects.get(pk=self.kwargs['call_part_pk'])

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'TODO3'}]
        # context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
        #                          {'name': f'Details ({file.call_part.call.little_name()})',
        #                           'url': url_call_parts_anchor},
        #                          {'name': file.name}]

        return context


class CallFileView(TemplateView):
    template_name = 'logged/call_part_file-detail.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        file = CallPartFile.objects.get(pk=self.kwargs['call_file_pk'])

        context['file'] = file

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        url_call_parts_anchor = reverse('logged-call-detail', kwargs={'pk': file.call_part.call.pk}) + '#parts'

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'Details ({file.call_part.call.little_name()})',
                                  'url': url_call_parts_anchor},
                                 {'name': f'Part {file.call_part.title}', 'url': reverse('logged-call-part-detail', kwargs={
                                     'call_pk': file.call_part.call.pk, 'call_part_pk': file.call_part.pk})},
                                 {'name': f'File ({file.name})'}]

        return context


class CallPartFileCreate(SuccessMessageMixin, CreateView):
    model = CallPartFile
    form_class = CallPartFileForm
    template_name = 'logged/call_part_file-form.tmpl'
    success_message = 'File added'

    def get_context_data(self, **kwargs):
        call = Call.objects.get(pk=self.kwargs['call_pk'])
        call_part: CallPart = CallPart.objects.get(pk=self.kwargs['call_part_pk'])

        context = super().get_context_data(**kwargs)

        context['call_part'] = call_part
        context['action'] = 'Create'

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'Details ({call.little_name()})',
                                  'url': reverse('logged-call-detail', kwargs={'pk': call.pk})},
                                 {'name': f'Call Part ({call_part.title})',
                                  'url': reverse('logged-call-part-detail', kwargs={'call_pk': call.pk,
                                                                                    'call_part_pk': call_part.pk
                                                                                    }
                                                 )
                                  },
                                 {'name': 'View Call Question'}
                                 ]

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['call_part_pk'] = self.kwargs['call_part_pk']
        return kwargs


class CallPartFileUpdate(SuccessMessageMixin, UpdateView):
    model = CallPartFile
    form_class = CallPartFileForm
    template_name = 'logged/call_part_file-form.tmpl'
    success_message = 'File updated'
    pk_url_kwarg = 'call_file_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'call-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'
                        })

        context['call_part'] = call_part = self.object.call_part
        context['action'] = 'Update'
        context['breadcrumb'] = [{'name': 'Calls', 'url': reverse('logged-calls')},
                                 {'name': f'Details ({call_part.call.little_name()})',
                                  'url': reverse('logged-call-update', kwargs={'pk': call_part.call.pk}) + '#parts'},
                                 {'name': 'TODO4'}
                                 ]

        return context

    def get_success_url(self):
        return reverse('logged-call-part-file-detail', kwargs={'call_pk': self.object.call_part.call.pk,
                                                               'call_file_pk': self.object.pk
                                                               })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['call_part_pk'] = self.object.call_part.pk
        return kwargs


class CallPartFileDelete(DeleteView, SuccessMessageMixin):
    pass
