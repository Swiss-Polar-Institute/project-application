from dal import autocomplete
from django.conf import settings
from django.contrib.auth.models import User

from project_core.models import OrganisationName, Source, KeywordUid, Keyword


class OrganisationsAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result):
        return result.name

    def get_queryset(self):
        qs = OrganisationName.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

    def has_add_permission(self, *args, **kwargs):
        # By default only authenticated users with permissions to add in the model
        # have the option to create keywords. We allow any user to create keywords
        return True

    def create_object(self, text):
        d = {self.create_field: text}

        return self.get_queryset().get_or_create(
            **d,
            defaults={'created_by': User.objects.get(username=settings.LOGGED_OUT_USERNAME)})[0]


class KeywordsAutocomplete(autocomplete.Select2QuerySetView):
    def create_object(self, text):
        source, created = Source.objects.get_or_create(source='External User')

        keyword_uuid, created = KeywordUid.objects.get_or_create(uid=None, source=source)

        d = {self.create_field: text,
             'description': 'User entered',
             'uid': keyword_uuid}

        return self.get_queryset().get_or_create(**d)[0]

    def get_result_label(self, result):
        return result.name

    def has_add_permission(self, *args, **kwargs):
        # By default only authenticated users with permissions to add in the model
        # have the option to create keywords. We allow any user to create keywords
        return True

    def get_queryset(self):
        qs = Keyword.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        qs = qs.order_by('name')
        return qs
