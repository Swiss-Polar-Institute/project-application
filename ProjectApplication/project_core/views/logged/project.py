from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from ProjectApplication import settings
from comments.utils import process_comment_attachment
from evaluation.forms.eligibility import EligibilityDecisionForm
from evaluation.models import Reviewer
from project_core.models import Proposal, Call, Project
from project_core.utils import user_is_in_group_name
from project_core.views.common.proposal import AbstractProposalDetailView, AbstractProposalView


class ProjectList(TemplateView):
    template_name = 'logged/project-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        call_id = self.request.GET.get('call', None)

        context['projects'] = Project.objects.all()

        context.update({'active_section': 'lists',
                        'active_subsection': 'project-list',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists', 'url': reverse('logged-project-list')},
                                 {'name': 'Projects'}]

        return context

