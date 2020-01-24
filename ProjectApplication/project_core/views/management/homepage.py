from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from project_core.templatetags.user_is_reviewer import user_is_reviewer
from django.http import HttpResponseRedirect


class Homepage(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if user_is_reviewer(request):
            return HttpResponseRedirect(reverse('management-proposals-list'))

        context['active_section'] = 'home'
        context['active_subsection'] = 'home'
        context['sidebar_template'] = 'management/_sidebar-homepage.tmpl'

        return render(request, 'management/homepage.tmpl', context)