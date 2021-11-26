from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView

from comments import utils
from comments.utils import process_comment_attachment
from project_core.forms.financial_key import FinancialKeyForm
from project_core.forms.user import UserForm
from project_core.models import Project, FinancialKey, SpiUser


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
                        'active_subsection': 'financial_key-list',
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'users',
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
                        'active_subsection': 'user-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-lists')},
                                 {'name': 'Users', 'url': reverse('logged-user-list')},
                                 {'name': 'Create'}]

        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('logged-user-detail', kwargs={'pk': self.object.pk})



class UserDetailView(DetailView):
    template_name = 'logged/user-view.tmpl'
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

        if user_password:
            if user_password_id == self.kwargs['pk']:
                context['new_password'] = self.request.session['user_password']

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
            self.request.session['user_password_user_id'] = self.kwargs['pk']
            self.request.session['user_password'] = form.new_password

        return result

