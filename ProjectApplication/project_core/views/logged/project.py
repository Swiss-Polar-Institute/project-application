from django.urls import reverse
from django.views.generic import DetailView, ListView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from comments import utils
from comments.utils import process_comment_attachment
from project_core.filters import ProjectFilterSet
from project_core.models import Project, GeographicalArea, FundingInstrument
from project_core.serializers import (
    ProjectSerializer, ProjectDetailSerializer, GeographicalAreaSerializer, FundingInstrumentSerializer
)


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
    queryset = Project.objects.exclude(status=Project.ABORTED).exclude(on_website=False)
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilterSet
    ordering_fields = ('start_date',)


class ProjectDetailAPI(RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_field = 'uuid'


class GeographicalListAPI(ListAPIView):
    queryset = GeographicalArea.objects.all()
    serializer_class = GeographicalAreaSerializer


class FundingInstrumentListAPI(ListAPIView):
    queryset = FundingInstrument.objects.all()
    serializer_class = FundingInstrumentSerializer


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
