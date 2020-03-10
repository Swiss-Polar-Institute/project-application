from django.views.generic import TemplateView

from project_core.models import Call


class CallList(TemplateView):
    template_name = 'external/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.open_calls()

        return context