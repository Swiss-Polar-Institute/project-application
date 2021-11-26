from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, CreateView
from rest_framework.generics import ListAPIView

from comments import utils
from comments.utils import process_comment_attachment
from project_core.forms.financial_key import FinancialKeyForm
from project_core.models import Project, FinancialKey
from project_core.serializers import ProjectSerializer
from project_core.filters import ProjectFilterSet


class ProjectList(ListView):
    template_name = 'logged/project-list.tmpl'
    context_object_name = 'projects'
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Projects'}]

        return context


class ProjectListAPI(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilterSet


class AbstractProjectView(DetailView):
    template_name = 'logged/project-detail.tmpl'
    model = Project
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context.update(utils.comments_attachments_forms('logged-project-comment-add', context['project']))

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Projects', 'url': reverse('logged-project-list')},
                                 {'name': f'Details ({context["project"].key_pi()})'}]

        return context


class ProjectDetailView(AbstractProjectView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ProjectCommentAdd(AbstractProjectView):
    def post(self, request, *args, **kwargs):
        self.object = Project.objects.get(pk=kwargs['pk'])
        context = super().get_context_data(**kwargs)

        result = process_comment_attachment(request, context, 'logged-project-detail',
                                            'logged-project-comment-add',
                                            'logged/project-detail.tmpl',
                                            context['project'])

        return result


class FinancialKeyListView(ListView):
    template_name = 'logged/financial_key-list.tmpl'
    context_object_name = 'financial_keys'
    model = FinancialKey

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'financial_key-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Financial keys'}]

        return context


class FinancialKeyAdd(SuccessMessageMixin, CreateView):
    template_name = 'logged/financial_key-form.tmpl'
    model = FinancialKey
    success_message = 'Financial key created'
    form_class = FinancialKeyForm
    success_url = reverse_lazy('logged-financial-key-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'financial_key-add',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Financial keys', 'url': reverse('logged-financial-key-list')},
                                 {'name': 'Create'}]

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)
