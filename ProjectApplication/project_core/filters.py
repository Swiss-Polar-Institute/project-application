from django.db.models import Q

from django_filters.rest_framework import CharFilter, FilterSet

from project_core.models import Project


class ProjectFilterSet(FilterSet):
    key_title = CharFilter(method='filter_key_title', label="Key or Title")
    keywords = CharFilter(method='filter_keywords')
    geographical_areas = CharFilter(method='filter_geographical_areas')
    start_date = CharFilter(method='filter_start_date')

    def filter_key_title(self, queryset, name, value):
        search_query = Q(
            Q(key__contains=value) |
            Q(title__contains=value)
        )
        return queryset.filter(search_query)

    def filter_keywords(self, queryset, name, value):
        return queryset.filter(keywords__name=value)

    def filter_geographical_areas(self, queryset, name, value):
        return queryset.filter(geographical_areas__name=value)

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(start_date__year=value)

    class Meta:
        model = Project
        fields = ('key_title', 'keywords', 'geographical_areas', 'start_date')
