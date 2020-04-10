from dal import autocomplete
from django.db.models import Q

from project_core.models import PhysicalPerson


class PhysicalPersonAutocomplete(autocomplete.Select2QuerySetView):
    # def get_result_label(self, result):
    #     return result.name

    def get_queryset(self):
        qs = PhysicalPerson.objects.all()

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(surname__icontains=self.q))

        qs = qs.order_by('first_name')
        return qs
