from django.urls import reverse
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from grant_management.forms.grant_agreement import GrantAgreementForm
from grant_management.forms.project import ProjectBasicInformationForm
from grant_management.models import GrantAgreement
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

        project = context['project']

        if hasattr(project, 'grantagreement'):
            context['grant_agreement_button_text'] = 'Edit Grant Agreement'
            context['grant_agreement_button_url'] = reverse('logged-grant_management-grant_agreement-update',
                                                            kwargs={'pk': project.grantagreement.id})
        else:
            context['grant_agreement_button_text'] = 'Create Grant Agreement'
            context['grant_agreement_button_url'] = reverse('logged-grant_management-grant_agreement-add',
                                                            kwargs={'project': project.id})

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


class GrantAgreementAddView(CreateView):
    template_name = 'grant_management/grant_agreement-form.tmpl'
    form_class = GrantAgreementForm
    model = GrantAgreement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_id = self.kwargs['project']

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': 'Project detail',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project_id})},
                                 {'name': 'Grant management edit'}]

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = Project.objects.get(id=self.kwargs['project'])
        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})


class GrantAgreementUpdateView(UpdateView):
    template_name = 'grant_management/grant_agreement-form.tmpl'
    form_class = GrantAgreementForm
    model = GrantAgreement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_id = context['grantagreement'].project.id

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': 'Project detail',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project_id})},
                                 {'name': 'Grant management create'}]

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = kwargs['instance'].project
        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})
