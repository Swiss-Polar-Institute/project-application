from django.views.generic import ListView

from project_core.models import Call


class CallList(ListView):
    template_name = 'external/call-list.tmpl'
    context_object_name = 'calls'
    model = Call

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_queryset(self):
        # Avoid using ListView.queryset. Call.open_calls() uses timezone.now().
        # If using ListView.queryset the queryset is retreived on the application startup
        # so calls that become open during the application startup would not appear here
        # (or calls that become closed after the application startup would not disappear).
        #
        # Another solution was to do the query in call.open_calls() like:
        #         from django.db.models.functions import Now
        #         return Call.objects.filter(call_open_date__lte=Now(),
        #                                    submission_deadline__gte=Now())
        # in this case the query has the variable CURRENT_TIMESTAMP and it works.
        # I chose to not use this method to avoid timezones problems between Django-MariaDB and
        # different deployments environment (e.g. Docker, system's timezone, etc.).
        #
        return Call.open_calls()
