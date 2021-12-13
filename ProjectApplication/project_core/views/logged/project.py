from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from rest_framework.generics import ListAPIView

from comments import utils
from comments.utils import process_comment_attachment
from evaluation.models import Reviewer
from project_core.filters import ProjectFilterSet
from project_core.forms.financial_key import FinancialKeyForm
from project_core.forms.user import UserForm
from project_core.models import Project, FinancialKey
from project_core.models import SpiUser
from project_core.serializers import ProjectSerializer


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
    queryset = Project.objects.exclude(status=Project.ABORTED)
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilterSet
    ordering_fields = ('start_date', )


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


class UserListView(ListView):
    template_name = 'logged/user-list.tmpl'
    context_object_name = 'users'
    model = SpiUser
    queryset = SpiUser.objects.filter(is_superuser=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'user-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Users'}]

        return context


class UserAdd(SuccessMessageMixin, CreateView):
    template_name = 'logged/user-form.tmpl'
    model = SpiUser
    success_message = 'User created'
    form_class = UserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'user-add',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Users', 'url': reverse('logged-user-list')},
                                 {'name': 'Create'}]

        return context

    def form_valid(self, form):
        result = super().form_valid(form)

        if form.new_password:
            self.request.session['user_password_user_id'] = form.user_id_new_password
            self.request.session['user_password'] = form.new_password

        return result

    def get_success_url(self, **kwargs):
        return reverse('logged-user-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        type_of_user = self.request.GET.get('type_of_user')

        if type_of_user:
            kwargs['type_of_user'] = type_of_user

        return kwargs


class UserDetailView(DetailView):
    template_name = 'logged/user-detail.tmpl'
    model = SpiUser
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'user-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Users', 'url': reverse('logged-user-list')},
                                 {'name': 'View'}]

        user_password = self.request.session.get('user_password')
        user_password_id = self.request.session.get('user_password_user_id')

        context['new_password'] = None

        if self.object.is_reviewer():
            context['physical_person'] = Reviewer.objects.get(user=self.object).person

        if user_password:
            if user_password_id == self.kwargs['pk']:
                context['new_password'] = self.request.session['user_password']
                # Changing the password on the view is horrible
                # but this allows changing the user's own password and visualise it before
                # the user is logged out
                #
                # In normal circumstances the users would have a different way to reset their own passwords
                # but we are keeping the flow for resetting users other passwords or own passwords similar
                # (due to time constraints for the project)
                self.object.set_password(context['new_password'])
                self.object.save()

                if self.object == self.request.user:
                    messages.warning(self.request,
                                     'Your own password has changed. You will be logged out and you will need '
                                     'to login again with the new password.')

            self.request.session['user_password'] = None
            self.request.session['user_password_user_id'] = None

        return context


class UserUpdate(UpdateView):
    template_name = 'logged/user-form.tmpl'
    model = User
    success_message = 'User updated'
    form_class = UserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'user-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Users', 'url': reverse('logged-user-list')},
                                 {'name': 'View'}]

        return context

    def get_success_url(self):
        return reverse('logged-user-detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        result = super().form_valid(form)

        if form.new_password:
            self.request.session['user_password_user_id'] = form.user_id_new_password
            self.request.session['user_password'] = form.new_password

        return result
