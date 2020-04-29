from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from grant_management.forms.blog_posts import BlogPostsFormSet, BlogPostsInlineFormSet
from grant_management.forms.financial_reports import FinancialReportsFormSet, FinancialReportsInlineFormSet
from grant_management.forms.grant_agreement import GrantAgreementForm
from grant_management.forms.invoices import InvoicesInlineFormSet, InvoicesFormSet
from grant_management.forms.lay_summaries import LaySummariesFormSet
from grant_management.forms.project_basic_information import ProjectBasicInformationForm
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
            context['grant_agreement_button_text'] = 'Edit'
            context['grant_agreement_button_url'] = reverse('logged-grant_management-grant_agreement-update',
                                                            kwargs={'pk': project.grantagreement.id})
        else:
            context['grant_agreement_button_text'] = 'Create'
            context['grant_agreement_button_url'] = reverse('logged-grant_management-grant_agreement-add',
                                                            kwargs={'project': project.id})

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})'}]

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
                                 {'name': f'Project detail ({project.call_pi()})',
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

        project = Project.objects.get(id=self.kwargs['project'])

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Grant management'}]

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

        project = context['grantagreement'].project

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Grant management'}]

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = kwargs['instance'].project
        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})


class BlogPostsUpdateView(TemplateView):
    @staticmethod
    def _cancel_url(kwargs):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': kwargs['project']})

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = BlogPostsUpdateView._cancel_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context[BlogPostsFormSet.FORM_NAME] = BlogPostsInlineFormSet(prefix=BlogPostsFormSet.FORM_NAME,
                                                                     instance=project)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Blog Posts'}]

        return render(request, 'grant_management/blog_posts-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = LaySummariesUpdateView._cancel_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        blog_posts_form = BlogPostsInlineFormSet(request.POST, request.FILES,
                                                 prefix=BlogPostsFormSet.FORM_NAME,
                                                 instance=project)

        if blog_posts_form.is_valid():
            blog_posts_form.save()
            return redirect(reverse('logged-grant_management-project-detail', kwargs={'pk': project.id}))

        messages.error(request, 'Lay Summaries not saved. Verify errors in the form')

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'BlogPosts'}]

        context[LaySummariesFormSet.FORM_NAME] = blog_posts_form

        context['project'] = project

        return render(request, 'grant_management/blog_posts-form.tmpl', context)


class LaySummariesUpdateView(TemplateView):
    @staticmethod
    def _cancel_url(kwargs):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': kwargs['project']})

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = LaySummariesUpdateView._cancel_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context[LaySummariesFormSet.FORM_NAME] = BlogPostsInlineFormSet(prefix=LaySummariesFormSet.FORM_NAME,
                                                                        instance=project)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Lay Summaries'}]

        return render(request, 'grant_management/lay_summaries-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = LaySummariesUpdateView._cancel_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        lay_summaries_form = BlogPostsInlineFormSet(request.POST, request.FILES,
                                                    prefix=LaySummariesFormSet.FORM_NAME,
                                                    instance=project)

        if lay_summaries_form.is_valid():
            lay_summaries_form.save()
            return redirect(reverse('logged-grant_management-project-detail', kwargs={'pk': project.id}))

        messages.error(request, 'Lay Summaries not saved. Verify errors in the form')

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Lay Summaries'}]

        context[LaySummariesFormSet.FORM_NAME] = lay_summaries_form

        context['project'] = project

        return render(request, 'grant_management/lay_summaries-form.tmpl', context)


class FinancesViewUpdate(TemplateView):
    @staticmethod
    def _cancel_url(kwargs):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': kwargs['project']})

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = FinancesViewUpdate._cancel_url(kwargs)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        project = Project.objects.get(id=kwargs['project'])

        context[InvoicesFormSet.FORM_NAME] = InvoicesInlineFormSet(prefix=InvoicesFormSet.FORM_NAME, instance=project)
        context[FinancialReportsFormSet.FORM_NAME] = FinancialReportsInlineFormSet(
            prefix=FinancialReportsFormSet.FORM_NAME, instance=project)

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Finances'}]

        return render(request, 'grant_management/finances-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = FinancesViewUpdate._cancel_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        invoices_form = InvoicesInlineFormSet(request.POST, request.FILES,
                                              prefix=InvoicesFormSet.FORM_NAME,
                                              instance=project)
        financial_reports_form = FinancialReportsInlineFormSet(request.POST, request.FILES,
                                                               prefix=FinancialReportsFormSet.FORM_NAME,
                                                               instance=project)

        if all([invoices_form.is_valid(), financial_reports_form.is_valid()]):
            invoices_form.save()
            financial_reports_form.save()
            return redirect(reverse('logged-grant_management-project-detail', kwargs={'pk': project.id}))

        messages.error(request, 'Finances not saved. Verify errors in the forms.')

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.call_pi()})',
                                  'url': reverse('logged-grant_management-project-detail',
                                                 kwargs={'pk': project.id})},
                                 {'name': 'Finances'}]

        context[InvoicesFormSet.FORM_NAME] = invoices_form
        context[FinancialReportsFormSet.FORM_NAME] = financial_reports_form

        context['project'] = project

        return render(request, 'grant_management/finances-form.tmpl', context)
