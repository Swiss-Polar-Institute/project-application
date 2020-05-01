from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from grant_management.forms.blog_posts import BlogPostsFormSet, BlogPostsInlineFormSet
from grant_management.forms.grant_agreement import GrantAgreementForm
from grant_management.forms.invoices import InvoicesInlineFormSet, InvoicesFormSet
from grant_management.forms.lay_summaries import LaySummariesFormSet, LaySummariesInlineFormSet
from grant_management.forms.project_basic_information import ProjectBasicInformationForm
from grant_management.forms.reports import FinancialReportsInlineFormSet, ScientificReportsInlineFormSet
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
                                 {'name': f'Project detail ({project.key_pi()})'}]

        context['lay_summaries_count'] = project.laysummary_set.exclude(text='').count()
        context['blog_posts_count'] = project.blogpost_set.exclude(text='').count()

        return context


class ProjectBasicInformationUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'grant_management/project-basic_information-form.tmpl'
    form_class = ProjectBasicInformationForm
    model = Project
    success_message = 'Project information updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['pk'])

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.key_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Project basic information Edit'}]

        context['project'] = project
        return context

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.pk})


def context_data_grant_greement(project):
    context = {'active_section': 'grant_management',
               'active_subsection': 'project-list',
               'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'}

    context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                             {'name': f'Project detail ({project.key_pi()})',
                              'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                             {'name': 'Grant management'}]

    context['project'] = project

    return context


class GrantAgreementAddView(SuccessMessageMixin, CreateView):
    template_name = 'grant_management/grant_agreement-form.tmpl'
    form_class = GrantAgreementForm
    model = GrantAgreement
    success_message = 'Grant agreement added'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['project'])

        context.update(context_data_grant_greement(project))

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = Project.objects.get(id=self.kwargs['project'])
        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})


class GrantAgreementUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'grant_management/grant_agreement-form.tmpl'
    form_class = GrantAgreementForm
    model = GrantAgreement
    success_message = 'Grant agreement updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = context['grantagreement'].project

        context.update(context_data_grant_greement(project))

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = kwargs['instance'].project
        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})


def grant_management_project_url(kwargs):
    return reverse('logged-grant_management-project-detail', kwargs={'pk': kwargs['project']})


class BlogPostsUpdateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = grant_management_project_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context[BlogPostsFormSet.FORM_NAME] = BlogPostsInlineFormSet(prefix=BlogPostsFormSet.FORM_NAME,
                                                                     instance=project)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.key_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Blog Posts'}]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context[BlogPostsFormSet.FORM_NAME] = BlogPostsInlineFormSet(prefix=BlogPostsFormSet.FORM_NAME,
                                                                     instance=context['project'])

        return render(request, 'grant_management/blog_posts-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        blog_posts_form = BlogPostsInlineFormSet(request.POST, request.FILES,
                                                 prefix=BlogPostsFormSet.FORM_NAME,
                                                 instance=context['project'])

        if blog_posts_form.is_valid():
            blog_posts_form.save()
            messages.success(request, 'Blog Posts saved')
            return redirect(grant_management_project_url(kwargs))

        messages.error(request, 'Blog Posts not saved. Verify errors in the form')

        context[BlogPostsFormSet.FORM_NAME] = blog_posts_form

        return render(request, 'grant_management/blog_posts-form.tmpl', context)


class LaySummariesUpdateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = grant_management_project_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.key_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Lay Summaries'}]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context[LaySummariesFormSet.FORM_NAME] = LaySummariesInlineFormSet(prefix=LaySummariesFormSet.FORM_NAME,
                                                                           instance=context['project'])

        return render(request, 'grant_management/lay_summaries-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        lay_summaries_form = LaySummariesInlineFormSet(request.POST, request.FILES,
                                                       prefix=LaySummariesFormSet.FORM_NAME,
                                                       instance=context['project'])

        if lay_summaries_form.is_valid():
            lay_summaries_form.save()
            messages.success(request, 'Lay Summaries saved')
            return redirect(grant_management_project_url(kwargs))

        messages.error(request, 'Lay Summaries not saved. Verify errors in the form')

        context[LaySummariesFormSet.FORM_NAME] = lay_summaries_form

        return render(request, 'grant_management/lay_summaries-form.tmpl', context)


class ScientificReportsUpdateView(TemplateView):
    FORM_NAME = 'scientific_reports_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = grant_management_project_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.key_pi()})',
                                  'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                                 {'name': 'Scientific reports'}]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context[ScientificReportsUpdateView.FORM_NAME] = ScientificReportsInlineFormSet(
            prefix=ScientificReportsUpdateView.FORM_NAME,
            instance=context['project'])

        return render(request, 'grant_management/scientific_reports-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        scientific_reports_form = ScientificReportsInlineFormSet(request.POST, request.FILES,
                                                                 prefix=ScientificReportsUpdateView.FORM_NAME,
                                                                 instance=context['project'])

        if scientific_reports_form.is_valid():
            scientific_reports_form.save()
            messages.success(request, 'Scientific Reports saved')
            return redirect(grant_management_project_url(kwargs))

        messages.error(request, 'Scientific reports not saved. Verify errors in the form')

        context[ScientificReportsUpdateView.FORM_NAME] = scientific_reports_form

        return render(request, 'grant_management/scientific_reports-form.tmpl', context)


class FinancesViewUpdate(TemplateView):
    FORM_NAME = 'financial_reports_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context['cancel_url'] = grant_management_project_url(kwargs)

        context.update({'active_section': 'grant_management',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'})

        context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                                 {'name': f'Project detail ({project.key_pi()})',
                                  'url': reverse('logged-grant_management-project-detail',
                                                 kwargs={'pk': project.id})},
                                 {'name': 'Finances'}]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context[InvoicesFormSet.FORM_NAME] = InvoicesInlineFormSet(prefix=InvoicesFormSet.FORM_NAME,
                                                                   instance=context['project'])
        context[FinancesViewUpdate.FORM_NAME] = FinancialReportsInlineFormSet(
            prefix='financial_reports_form', instance=context['project'])

        return render(request, 'grant_management/finances-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        invoices_form = InvoicesInlineFormSet(request.POST, request.FILES,
                                              prefix=InvoicesFormSet.FORM_NAME,
                                              instance=context['project'])
        financial_reports_form = FinancialReportsInlineFormSet(request.POST, request.FILES,
                                                               prefix='financial_reports_form',
                                                               instance=context['project'])

        if all([invoices_form.is_valid(), financial_reports_form.is_valid()]):
            invoices_form.save()
            financial_reports_form.save()
            messages.success(request, 'Finances updated')
            return redirect(reverse('logged-grant_management-project-detail', kwargs={'pk': context['project'].id}))

        messages.error(request, 'Finances not saved. Verify errors in the forms.')

        context[InvoicesFormSet.FORM_NAME] = invoices_form
        context[FinancesViewUpdate.FORM_NAME] = financial_reports_form

        return render(request, 'grant_management/finances-form.tmpl', context)
