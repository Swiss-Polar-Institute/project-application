from datetime import date

from django.test import TestCase

from grant_management.forms.publications import PublicationModelForm
from grant_management.models import SocialNetwork, Publication
from project_core.tests import database_population


class PublicationModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_publication_valid(self):
        social_network, _ = SocialNetwork.objects.get_or_create(name='Twitter')

        data = {'project': self._project,
                'doi': 'da942924k/dkd3',
                'reference': 'John Doe and James Smith, Very interesting article, 2020',
                'title': 'Very interesting article',
                'published_date': date(2020, 5, 5)
                }

        self.assertEqual(Publication.objects.all().count(), 0)
        publication_form = PublicationModelForm(data=data)
        self.assertTrue(publication_form.is_valid())
        publication_form.save()
        self.assertEqual(Publication.objects.all().count(), 1)
