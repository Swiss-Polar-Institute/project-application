from django.db.models import Q

from rest_framework import serializers

from project_core.models import Project, Keyword, GeographicalArea, PersonPosition, OrganisationName
from grant_management.models import Location, Medium, LaySummary


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('name', )


class GeographicalAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicalArea
        fields = ('name', )


class OrganisationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationName
        fields = ('name', )


class PersonPositionSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='person.full_name')
    organisation_names = OrganisationNameSerializer(many=True, read_only=True)

    class Meta:
        model = PersonPosition
        fields = ('full_name', 'organisation_names')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude', )


class FilterMediumSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(~Q(license_id=None))
        return super(FilterMediumSerializer, self).to_representation(data)


class MediumSerializer(serializers.ModelSerializer):
    photographer = serializers.CharField(source='photographer.full_name')

    class Meta:
        model = Medium
        fields = ('photographer', 'file', )
        list_serializer_class = FilterMediumSerializer


class FilterLaySummarySerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(lay_summary_type__name="Web")
        return super(FilterLaySummarySerializer, self).to_representation(data)


class LaySummarySerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.full_name')
    class Meta:
        model = LaySummary
        fields = ('text', 'author', )
        list_serializer_class = FilterLaySummarySerializer


class ProjectSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)
    geographical_areas = GeographicalAreaSerializer(many=True, read_only=True)
    principal_investigator = PersonPositionSerializer(read_only=True)
    project_location = LocationSerializer(many=True, read_only=True)
    medium_set = MediumSerializer(many=True, read_only=True)
    laysummary_set = LaySummarySerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('uuid', 'key', 'title', 'keywords', 'geographical_areas', 'location',
                  'start_date', 'end_date', 'principal_investigator', 'project_location',
                  'medium_set', 'laysummary_set'
                  )
