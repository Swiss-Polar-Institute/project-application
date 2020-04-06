from django.urls import reverse
from django.views.generic import TemplateView, DetailView, UpdateView

from grant_management.forms.project import ProjectBasicInformationForm
from project_core.models import Project


class ProjectList(TemplateView):
    template_name = 'grant_management/project-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['projects_active'] = Project.objects.all().filter(status=Project.ONGOING)
        context['projects_inactive'] = Project.objects.all().exclude(status=Project.ONGOING)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Grant management'}]

        return context


class ProjectDetail(DetailView):
    template_name = 'grant_management/project-detail.tmpl'
    context_object_name = 'project'
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': 'Project detail'}]

        return context


class ProjectBasicInformationUpdateView(UpdateView):
    template_name = 'grant_management/project-basic_information-form.tmpl'
    form_class = ProjectBasicInformationForm
    model = Project
    success_url = 'https://www.google.com'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['pk'])

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': 'Project detail',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Project basic information Edit'}]

        context['project'] = project
        return context

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.pk})
