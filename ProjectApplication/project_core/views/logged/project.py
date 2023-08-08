from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response

from comments import utils
from comments.utils import process_comment_attachment
from project_core.filters import ProjectFilterSet
from project_core.models import Project, GeographicalArea, FundingInstrument, Trace, TraceCoordinates
from project_core.serializers import (
    ProjectSerializer, ProjectDetailSerializer, GeographicalAreaSerializer, FundingInstrumentSerializer,
    TraceListSerializer, TraceDetailSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


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


class ProjectLoggedAPI(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ProjectMediaGalleryAPI(APIView):
    def get(self, request):
        cookies = request.COOKIES
        response = HttpResponseRedirect(
            f'https://media.swisspolar.ch/cookie?csrftoken={cookies.get("csrftoken")}&sessionid={cookies.get("sessionid")}')
        return response


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
    pagination_class = StandardResultsSetPagination


class FundingInstrumentListAPI(ListAPIView):
    queryset = FundingInstrument.objects.all()
    serializer_class = FundingInstrumentSerializer
    pagination_class = StandardResultsSetPagination


class TraceListAPI(ListCreateAPIView):
    queryset = Trace.objects.all()
    serializer_class = TraceListSerializer

    def post(self, request, *args, **kwargs):
        trace_coordinates = request.data.pop("trace_coordinates")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trace = serializer.save()
        headers = self.get_success_headers(serializer.data)

        for coordinate in trace_coordinates:
            TraceCoordinates(
                lng=coordinate["lng"],
                lat=coordinate["lat"],
                trace=trace
            ).save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TraceDetailAPI(RetrieveAPIView):
    queryset = Trace.objects.all()
    serializer_class = TraceDetailSerializer
    lookup_field = 'id'


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
