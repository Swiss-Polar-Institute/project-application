from dal import autocomplete
from django.db.models import Value as V
from django.db.models.functions import Concat

from project_core.models import PhysicalPerson, PersonPosition


class PhysicalPersonAutocomplete(autocomplete.Select2QuerySetView):
    # def get_result_label(self, result):
    #     return result.name

    def get_queryset(self):
        qs = PhysicalPerson.objects.\
            all(). \
            annotate(full_name=Concat('first_name', V(' '), 'surname'))

        if self.q:
            qs = qs.filter(full_name__icontains=self.q)

        qs = qs.order_by('full_name')
        return qs


class PersonPositionsAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result: PersonPosition):

        organisations_ordered = result.organisations_ordered_by_name_str()

        organisations_group = ''

        if organisations_ordered:
            organisations_group = f'{organisations_ordered}'

        if result.group:
            if organisations_group:
                organisations_group += '. '

            organisations_group += f'Group: {result.group}'


        return f'{result.academic_title} {result.person.first_name} {result.person.surname} ({organisations_group})'

    def get_queryset(self):
        qs = PersonPosition.objects.\
            filter(privacy_policy=True).\
            annotate(full_name=Concat('person__first_name', V(' '), 'person__surname'))

        if self.q:
            qs = qs.filter(full_name__icontains=self.q)

        qs = qs.order_by('full_name')
        return qs
