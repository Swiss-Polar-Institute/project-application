from django.shortcuts import render
from django.views.generic import TemplateView


class ListsView(TemplateView):
    template_name = 'logged/lists.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'lists',
                        'active_subsection': 'lists',
                        'sidebar_template': 'logged/_sidebar-lists.tmpl'})

        context['breadcrumb'] = [{'name': 'Lists'}]

        return context
