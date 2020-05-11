from django.test import TestCase

from project_core.models import Keyword, OrganisationName
from project_core.tests import database_population
from project_core.views.common.autocomplete import OrganisationsAutocomplete, KeywordsAutocomplete


class OrganisationsAutocompleteTest(TestCase):
    def setUp(self):
        database_population.create_organisation_names()
        self._organisations_autocomplete = OrganisationsAutocomplete(create_field='name')

    def test_get_query(self):
        self._organisations_autocomplete.q = ''
        query_set = self._organisations_autocomplete.get_queryset()
        self.assertEqual(query_set.count(), 2)

        self._organisations_autocomplete.q = 'EPFL'
        query_set = self._organisations_autocomplete.get_queryset()
        self.assertEqual(query_set.count(), 1)

    def test_create_object(self):
        new_organisation = 'this_is_organisation_from_unittest'
        self.assertEqual(OrganisationName.objects.filter(name=new_organisation).count(), 0)

        self._organisations_autocomplete.q = new_organisation
        self._organisations_autocomplete.create_object(new_organisation)

        self.assertEqual(OrganisationName.objects.filter(name=new_organisation).count(), 1)


class KeywordsAutocompleteTest(TestCase):
    def setUp(self):
        database_population.create_keywords()
        self._keywords_autocomplete = KeywordsAutocomplete(create_field='name')

    def test_get_query(self):
        self._keywords_autocomplete.q = ''
        query_set = self._keywords_autocomplete.get_queryset()
        self.assertEqual(query_set.count(), 8)

        self._keywords_autocomplete.q = 'algae'
        query_set = self._keywords_autocomplete.get_queryset()
        self.assertEqual(query_set.count(), 1)

    def test_create_object(self):
        new_keyword = 'this_is_keyword_from_unittest'
        self.assertEqual(Keyword.objects.filter(name=new_keyword).count(), 0)

        self._keywords_autocomplete.q = new_keyword
        self._keywords_autocomplete.create_object(new_keyword)

        self.assertEqual(Keyword.objects.filter(name=new_keyword).count(), 1)
