from dal import autocomplete
from django.db.models import Value as V
from django.db.models.functions import Concat

from project_core.models import PhysicalPerson


class PhysicalPersonAutocomplete(autocomplete.Select2QuerySetView):
    # def get_result_label(self, result):
    #     return result.name

    def get_queryset(self):
        qs = PhysicalPerson.objects.all()

        if self.q:
            qs = PhysicalPerson.objects.annotate(full_name=Concat('first_name', V(' '), 'surname')).filter(
                full_name__icontains=self.q)

        qs = qs.order_by('first_name')
        return qs
