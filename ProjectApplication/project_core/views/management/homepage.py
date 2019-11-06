from django.shortcuts import render
from django.views.generic import TemplateView


class Homepage(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'home'
        context['active_subsection'] = 'home'
        context['sidebar_template'] = 'management/_sidebar-homepage.tmpl'

        return render(request, 'management/homepage.tmpl', context)