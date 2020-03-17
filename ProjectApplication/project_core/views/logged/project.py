from django.urls import reverse
from django.urls import reverse
from django.views.generic import TemplateView, DetailView

from project_core.models import Project


class ProjectList(TemplateView):
    template_name = 'logged/project-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        call_id = self.request.GET.get('call', None)

        context['projects'] = Project.objects.all()

        context.update({'active_section': 'lists',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Projects'}]

        return context


class ProjectDetailView(DetailView):
    template_name = 'logged/project-detail.tmpl'
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Projects', 'url': reverse('logged-project-list')},
                                 {'name': 'Details'}]

        return context
