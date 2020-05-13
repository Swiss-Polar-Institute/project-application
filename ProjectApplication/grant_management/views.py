from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from grant_management.forms.blog_posts import BlogPostsFormSet, BlogPostsInlineFormSet
from grant_management.forms.grant_agreement import GrantAgreementForm
from grant_management.forms.installments import InstallmentsFormSet, InstallmentsInlineFormSet
from grant_management.forms.invoices import InvoicesInlineFormSet, InvoicesFormSet
from grant_management.forms.lay_summaries import LaySummariesFormSet, LaySummariesInlineFormSet
from grant_management.forms.project_basic_information import ProjectBasicInformationForm
from grant_management.forms.reports import FinancialReportsInlineFormSet, ScientificReportsInlineFormSet, ReportsFormSet
from grant_management.models import GrantAgreement
from project_core.models import Project
from .forms.datasets import DatasetsFormSet, DatasetInlineFormSet
from .forms.media import MediaInlineFormSet, MediaFormSet
from .forms.project import ProjectForm
from .forms.publications import PublicationsInlineFormSet


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


class ProjectUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'grant_management/project-form.tmpl'
    form_class = ProjectForm
    model = Project
    success_message = 'Project updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Projects', 'url': reverse('logged-project-list')},
                                 {'name': f'Project update ({context["object"].key_pi()})'}]

        return context

    def get_success_url(self):
        return reverse('logged-project-detail', kwargs={'pk': self.object.pk})


class ProjectBasicInformationUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'grant_management/project-basic_information-form.tmpl'
    form_class = ProjectBasicInformationForm
    model = Project
    success_message = 'Project information updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['pk'])

        context.update(basic_context_data_grant_agreement(project, 'Edit project basic information'))

        context['project'] = project
        return context

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.pk})


def basic_context_data_grant_agreement(project, active_page):
    context = {'active_section': 'grant_management',
               'active_subsection': 'project-list',
               'sidebar_template': 'grant_management/_sidebar-grant_management.tmpl'}

    context['breadcrumb'] = [{'name': 'Grant management', 'url': reverse('logged-grant_management-project-list')},
                             {'name': f'Project detail ({project.key_pi()})',
                              'url': reverse('logged-grant_management-project-detail', kwargs={'pk': project.id})},
                             {'name': active_page}]

    return context


class GrantAgreementAddView(SuccessMessageMixin, CreateView):
    template_name = 'grant_management/grant_agreement-form.tmpl'
    form_class = GrantAgreementForm
    model = GrantAgreement
    success_message = 'Grant agreement added'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['project'])
        context['project'] = project

        context.update(basic_context_data_grant_agreement(project, 'Grant agreement'))

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
        context['project'] = project

        context.update(basic_context_data_grant_agreement(project, 'Grant agreement'))

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = kwargs['instance'].project
        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})


def grant_management_project_url(kwargs):
    return reverse('logged-grant_management-project-detail', kwargs={'pk': kwargs['project']})


class GrantManagementUpdateView(TemplateView):
    def __init__(self, *args, **kwargs):
        self._inline_formset = kwargs.pop('inline_formset')
        self._human_type = kwargs.pop('human_type')

        self.template_name = 'grant_management/generic-formset.tmpl'

        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = grant_management_project_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context.update(basic_context_data_grant_agreement(project, self._human_type.capitalize()))

        context['FORM_SET'] = self._inline_formset(prefix='FORM_SET', instance=context['project'])
        context['title'] = self._human_type.capitalize()
        context['save_text'] = f'Save {self._human_type.title()}'

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        forms = self._inline_formset(request.POST, request.FILES, prefix='FORM_SET',
                                     instance=context['project'])

        if forms.is_valid():
            forms.save()
            messages.success(request, f'{self._human_type.capitalize()} saved')
            return redirect(grant_management_project_url(kwargs))

        messages.error(request, f'{self._human_type.capitalize()} not saved. Verify errors in the form')

        context['FORM_SET'] = forms

        return render(request, self.template_name, context)


class BlogPostsUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=BlogPostsInlineFormSet,
                         human_type='blog posts'
                         )


class LaySummariesUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=LaySummariesInlineFormSet,
                         human_type='lay summaries'
                         )


class DatasetUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=DatasetInlineFormSet,
                         human_type='data'
                         )

class PublicationsUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=PublicationsInlineFormSet,
                         human_type='publications'
                         )

class MediaUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=MediaInlineFormSet,
                         human_type='media'
                         )


class InstallmentsUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=InstallmentsInlineFormSet,
                         human_type='installments'
                         )


class ScientificReportsUpdateView(GrantManagementUpdateView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         inline_formset=ScientificReportsInlineFormSet,
                         human_type='scientific reports'
                         )


class FinancesViewUpdate(TemplateView):
    FORM_NAME = 'financial_reports_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context['cancel_url'] = grant_management_project_url(kwargs)

        context.update(basic_context_data_grant_agreement(project, 'Finances'))

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
                                              instance=context['project'],
                                              form_kwargs={'user': request.user})

        financial_reports_form = FinancialReportsInlineFormSet(request.POST, request.FILES,
                                                               prefix='financial_reports_form',
                                                               instance=context['project'],
                                                               form_kwargs={'user': request.user})

        if all([invoices_form.is_valid(), financial_reports_form.is_valid()]):
            invoices_form.save()
            financial_reports_form.save()
            messages.success(request, 'Finance details saved')
            return redirect(reverse('logged-grant_management-project-detail', kwargs={'pk': context['project'].id}))

        messages.error(request, 'Finance details not saved. Verify errors in the forms')

        context[InvoicesFormSet.FORM_NAME] = invoices_form
        context[FinancesViewUpdate.FORM_NAME] = financial_reports_form

        return render(request, 'grant_management/finances-form.tmpl', context)


class LaySummariesRaw(TemplateView):
    template_name = 'grant_management/lay_summaries-raw.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call_id = kwargs['call']

        projects = Project.objects.filter(call_id=call_id).order_by('key')

        context['projects'] = projects

        return context
