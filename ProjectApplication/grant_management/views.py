from dal import autocomplete
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
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
from project_core.views.common.formset_inline_view import InlineFormsetUpdateView
from .forms.close_project import CloseProjectModelForm
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

        context.update(comments_attachments_forms('logged-grant_management-project-comment-add', project))

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
    pk_url_kwarg = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['project'])

        context.update(basic_context_data_grant_agreement(project, 'Basic project information'))

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


class AbstractGrantAgreement(SuccessMessageMixin, CreateView):
    template_name = 'grant_management/grant_agreement-form.tmpl'
    form_class = GrantAgreementForm
    model = GrantAgreement

    def _get_project(self):
        kwargs = self.kwargs

        if 'pk' in kwargs:
            project = GrantAgreement.objects.get(id=self.kwargs['pk']).project
        elif 'project' in kwargs:
            project = Project.objects.get(id=self.kwargs['project'])
        else:
            assert False

        return project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['project'] = self._get_project()

        context.update(basic_context_data_grant_agreement(context['project'], 'Grant agreement'))

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self._get_project()

        if 'pk' in self.kwargs:
            kwargs['instance'] = GrantAgreement.objects.get(id=self.kwargs['pk'])

        return kwargs

    def get_success_url(self):
        return reverse('logged-grant_management-project-detail', kwargs={'pk': self.object.project.pk})


class GrantAgreementAddView(AbstractGrantAgreement):
    success_message = 'Grant agreement added'


class GrantAgreementUpdateView(AbstractGrantAgreement):
    success_message = 'Grant agreement updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(context['project'], 'grantagreement'):
            context.update(comments_attachments_forms('logged-grant_management-grant_agreement-comment-add',
                                                      context['project'].grantagreement))

        return context


def grant_management_project_url(kwargs):
    return reverse('logged-grant_management-project-detail', kwargs={'pk': kwargs['project']})


class GrantManagementInlineFormset(InlineFormsetUpdateView):
    parent = Project
    url_id = 'project'
    tab = 'None'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.parent.objects.get(id=kwargs['project'])

        context.update(basic_context_data_grant_agreement(project, self.human_type_plural.capitalize()))

        context['project'] = project

        context['destination_url'] = reverse('logged-grant_management-project-detail',
                                             kwargs={'pk': project.id}) + f'?tab={self.tab}'

        context['FORM_SET'] = self.inline_formset(prefix='FORM_SET', instance=project)

        return context


class BlogPostsUpdateView(GrantManagementInlineFormset):
    inline_formset = BlogPostsInlineFormSet
    human_type = 'blog post'
    tab = 'deliverables'


class LaySummariesUpdateView(GrantManagementInlineFormset):
    inline_formset = LaySummariesInlineFormSet
    human_type = 'lay summary'
    human_type_plural = 'lay summaries'
    tab = 'deliverables'


class DatasetUpdateView(GrantManagementInlineFormset):
    inline_formset = DatasetInlineFormSet
    human_type = 'dataset'
    tab = 'deliverables'


class PublicationsUpdateView(GrantManagementInlineFormset):
    inline_formset = PublicationsInlineFormSet
    human_type = 'publication'
    tab = 'deliverables'


class MediaUpdateView(GrantManagementInlineFormset):
    inline_formset = MediaInlineFormSet
    human_type = 'medium'
    human_type_plural = 'media'
    tab = 'deliverables'


class InvoicesUpdateView(GrantManagementInlineFormset):
    inline_formset = InvoicesInlineFormSet
    human_type = 'invoice'
    tab = 'finances'


class FinancialReportsUpdateView(GrantManagementInlineFormset):
    inline_formset = FinancialReportsInlineFormSet
    human_type = 'financial report'
    tab = 'finances'


class InstallmentsUpdateView(GrantManagementInlineFormset):
    inline_formset = InstallmentsInlineFormSet
    human_type = 'installment'
    tab = 'finances'


class ScientificReportsUpdateView(GrantManagementInlineFormset):
    inline_formset = ScientificReportsInlineFormSet
    human_type = 'scientific report'
    tab = 'deliverables'


class SocialMediaUpdateView(GrantManagementInlineFormset):
    inline_formset = SocialNetworksInlineFormSet
    human_type = 'social medium'
    human_type_plural = 'social media'
    tab = 'deliverables'


class MilestoneUpdateView(GrantManagementInlineFormset):
    inline_formset = MilestoneInlineFormSet
    human_type = 'milestone'
    tab = 'deliverables'


class CloseProjectView(TemplateView):
    template_name = 'grant_management/close_project-form.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['project'] = Project.objects.get(id=kwargs['project'])

        context.update(basic_context_data_grant_agreement(context['project'], 'Grant agreement'))

        context['close_project_form'] = CloseProjectModelForm(instance=context['project'])

        return context

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project'])
        close_project_form = CloseProjectModelForm(request.POST, instance=project)

        if close_project_form.is_valid():
            close_project_form.save()
            messages.success(request, 'The project has been closed')
            return redirect(reverse('logged-grant_management-project-list'))

        context = self.get_context_data(**kwargs)
        context['close_project_form'] = close_project_form

        return render(request, 'grant_management/close_project-form.tmpl', context)


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


class GrantAgreementCommentAdd(AbstractGrantAgreement):
    def post(self, request, *args, **kwargs):
        self.object = Project.objects.get(pk=kwargs['pk'])
        context = super().get_context_data(**kwargs)

        result = process_comment_attachment(request, context, 'logged-grant_management-grant_agreement-update',
                                            'logged-grant_management-grant_agreement-comment-add',
                                            'grant_management/grant_agreement-form.tmpl',
                                            context['project'].grantagreement)

        return result
