from django.db.models import Q

from django_filters.rest_framework import CharFilter, FilterSet

from project_core.models import Project


class ProjectFilterSet(FilterSet):
    key_title = CharFilter(method='filter_any', label="Key, Title, Keyword, PI, laysummary or organisation")
    geographical_areas = CharFilter(method='filter_geographical_areas')
    funding_instrument = CharFilter(method='filter_funding_instrument')
    start_date = CharFilter(method='filter_start_date')

    def filter_any(self, queryset, name, value):
        search_query = Q(
            Q(key__icontains=value) |
            Q(title__icontains=value) |
            Q(keywords__name__icontains=value) |
            Q(principal_investigator__person__first_name__icontains=value) |
            Q(principal_investigator__person__surname__icontains=value) |
            Q(laysummary__text__icontains=value) |
            Q(principal_investigator__organisation_names__name__icontains=value)

        )
        return queryset.filter(search_query)

    def filter_geographical_areas(self, queryset, name, value):
        return queryset.filter(geographical_areas__name=value)

    def filter_funding_instrument(self, queryset, name, value):
        return queryset.filter(funding_instrument__long_name=value)

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(start_date__year=value)

    class Meta:
        model = Project
        fields = ('key_title', 'geographical_areas', 'funding_instrument', 'start_date')
