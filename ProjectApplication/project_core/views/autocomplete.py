from dal import autocomplete

from project_core.models import Organisation, Source, KeywordUid, Keyword


class OrganisationsAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result):
        return result.long_name

    def get_queryset(self):
        qs = Organisation.objects.all()

        if self.q:
            qs = qs.filter(long_name__icontains=self.q)

        return qs


class KeywordsAutocomplete(autocomplete.Select2QuerySetView):
    def create_object(self, text):
        source, created = Source.objects.get_or_create(source='External User')

        keyword_uuid, created = KeywordUid.objects.get_or_create(uid=None, source=source)

        d = {self.create_field: text,
             'description': 'User entered',
             'uid': keyword_uuid}

        return self.get_queryset().get_or_create(
            **d)[0]

    def get_result_label(self, result):
        return result.name

    def get_queryset(self):
        qs = Keyword.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        qs = qs.order_by('name')
        return qs