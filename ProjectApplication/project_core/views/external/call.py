from django.views.generic import ListView

from project_core.models import Call


class CallList(ListView):
    template_name = 'external/call-list.tmpl'
    context_object_name = 'calls'
    model = Call
    queryset = Call.open_calls()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
