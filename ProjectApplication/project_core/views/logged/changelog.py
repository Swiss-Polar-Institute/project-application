from django.shortcuts import render
from django.views.generic import TemplateView


class Changelog(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'home',
                        'active_subsection': 'changelog',
                        'sidebar_template': 'logged/_sidebar-home.tmpl'
                        })

        context['breadcrumb'] = [{'name': 'Changelog'}]

        return render(request, 'logged/changelog.tmpl', context)
