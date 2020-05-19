from dal import autocomplete
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from comments.utils import comments_attachments_forms, process_comment_attachment
from grant_management.forms.blog_posts import BlogPostsInlineFormSet
from grant_management.forms.grant_agreement import GrantAgreementForm
from grant_management.forms.installments import InstallmentsInlineFormSet
from grant_management.forms.invoices import InvoicesInlineFormSet
from grant_management.forms.lay_summaries import LaySummariesInlineFormSet
from grant_management.forms.project_basic_information import ProjectBasicInformationForm
from grant_management.forms.reports import FinancialReportsInlineFormSet, ScientificReportsInlineFormSet
from grant_management.models import GrantAgreement, MilestoneCategory
from project_core.models import Project
from .forms.datasets import DatasetInlineFormSet
from .forms.media import MediaInlineFormSet
from .forms.milestones import MilestoneInlineFormSet
from .forms.project import ProjectForm
from .forms.publications import PublicationsInlineFormSet
from .forms.social_network import SocialNetworksInlineFormSet


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
                                 {'name': f'Details ({project.key_pi()})'}]

        context['lay_summaries_count'] = project.laysummary_set.exclude(text='').count()
        context['blog_posts_count'] = project.blogpost_set.exclude(text='').count()

        context.update(comments_attachments_forms('logged-grant_management-project-comment-add-detail', project))

        if 'tab' in self.request.GET:
            context['active_tab'] = self.request.GET['tab']
        else:
            context['active_tab'] = 'finances'

        return context


class ProjectDetailCommentAdd(ProjectDetail):
    def post(self, request, *args, **kwargs):
        self.object = Project.objects.get(pk=kwargs['pk'])
        context = super().get_context_data(**kwargs)

        result = process_comment_attachment(request, context, 'logged-grant_management-project-detail',
                                            'logged-grant_management-project-comment-add-detail',
                                            'grant_management/project-detail.tmpl',
                                            context['project'])

        return result


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
                                 {'name': f'Edit ({context["object"].key_pi()})'}]

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
                             {'name': f'Details ({project.key_pi()})',
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
    inline_formset = None
    human_type = None
    tab = None

    def __init__(self, *args, **kwargs):
        self.template_name = 'grant_management/generic-formset.tmpl'

        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cancel_url'] = grant_management_project_url(kwargs)

        project = Project.objects.get(id=kwargs['project'])

        context['project'] = project

        context.update(basic_context_data_grant_agreement(project, self.human_type.capitalize()))

        context['FORM_SET'] = self.inline_formset(prefix='FORM_SET', instance=context['project'])
        context['title'] = self.human_type.capitalize()
        context['save_text'] = f'Save {self.human_type.title()}'

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form_kwargs = {}

        if hasattr(self.inline_formset, 'wants_user') and self.inline_formset.wants_user:
            form_kwargs = {'user': request.user}

        forms = self.inline_formset(request.POST, request.FILES, prefix='FORM_SET',
                                    instance=context['project'],
                                    form_kwargs=form_kwargs)

        if forms.is_valid():
            forms.save()
            messages.success(request, f'{self.human_type.capitalize()} saved')
            return redirect(f'{grant_management_project_url(kwargs)}?tab={self.tab}')

        messages.error(request, f'{self.human_type.capitalize()} not saved. Verify errors in the form')

        context['FORM_SET'] = forms

        return render(request, self.template_name, context)


class BlogPostsUpdateView(GrantManagementUpdateView):
    inline_formset = BlogPostsInlineFormSet
    human_type = 'blog posts'
    tab = 'deliverables'


class LaySummariesUpdateView(GrantManagementUpdateView):
    inline_formset = LaySummariesInlineFormSet
    human_type = 'lay summaries'
    tab = 'deliverables'


class DatasetUpdateView(GrantManagementUpdateView):
    inline_formset = DatasetInlineFormSet
    human_type = 'dataset'
    tab = 'deliverables'


class PublicationsUpdateView(GrantManagementUpdateView):
    inline_formset = PublicationsInlineFormSet
    human_type = 'publications'
    tab = 'deliverables'


class MediaUpdateView(GrantManagementUpdateView):
    inline_formset = MediaInlineFormSet
    human_type = 'media'
    tab = 'deliverables'


class InvoicesUpdateView(GrantManagementUpdateView):
    inline_formset = InvoicesInlineFormSet
    human_type = 'invoices'
    tab = 'finances'


class FinancialReportsUpdateView(GrantManagementUpdateView):
    inline_formset = FinancialReportsInlineFormSet
    human_type = 'financial reports'
    tab = 'finances'


class InstallmentsUpdateView(GrantManagementUpdateView):
    inline_formset = InstallmentsInlineFormSet
    human_type = 'installments'
    tab = 'finances'


class ScientificReportsUpdateView(GrantManagementUpdateView):
    inline_formset = ScientificReportsInlineFormSet
    human_type = 'scientific reports'
    tab = 'deliverables'


class SocialMediaUpdateView(GrantManagementUpdateView):
    inline_formset = SocialNetworksInlineFormSet
    human_type = 'social media'
    tab = 'deliverables'


class MilestoneUpdateView(GrantManagementUpdateView):
    inline_formset = MilestoneInlineFormSet
    human_type = 'milestones'
    tab = 'deliverables'


class LaySummariesRaw(TemplateView):
    template_name = 'grant_management/lay_summaries-raw.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        call_id = kwargs['call']

        projects = Project.objects.filter(call_id=call_id).order_by('key')

        context['projects'] = projects

        return context


class MilestoneCategoriesAutocomplete(autocomplete.Select2QuerySetView):
    def create_object(self, text):
        d = {self.create_field: text,
             'created_by': self.request.user}

        return self.get_queryset().get_or_create(**d)[0]

    def get_result_label(self, result):
        return result.name

    def has_add_permission(self, *args, **kwargs):
        # By default only authenticated users with permissions to add in the model
        # have the option to create keywords. We allow any user (if it's logged-in, for the URL)
        # to create milestones
        return True

    def get_queryset(self):
        qs = MilestoneCategory.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        qs = qs.order_by('name')
        return qs
