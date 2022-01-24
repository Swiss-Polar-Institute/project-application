from functools import reduce
from operator import or_

from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet

from project_core.models import Project


class ProjectFilterSet(FilterSet):
    key_any = CharFilter(method='filter_any', label="Key, Title, Keyword, PI, Lay summary or Organisation")
    geographical_areas = CharFilter(method='filter_geographical_areas')
    funding_instrument = CharFilter(method='filter_funding_instrument')
    start_date = CharFilter(method='filter_start_date')

    def filter_any(self, queryset, name, value):
        fields = [
            "key", "title", "keywords__name",
            "principal_investigator__person__first_name",
            "principal_investigator__person__surname",
            "laysummary__text", "principal_investigator__organisation_names__name"
        ]
        q_field = reduce(or_, (Q(**{f"{field}__icontains": word}) for word in value.split() for field in fields))
        print(queryset.filter(q_field))

        return queryset.filter(q_field).distinct()

    def filter_geographical_areas(self, queryset, name, value):
        return queryset.filter(geographical_areas__name=value)

    def filter_funding_instrument(self, queryset, name, value):
        return queryset.filter(funding_instrument__long_name=value)

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(start_date__year=value)

    class Meta:
        model = Project
        fields = ('key_any', 'geographical_areas', 'funding_instrument', 'start_date')
