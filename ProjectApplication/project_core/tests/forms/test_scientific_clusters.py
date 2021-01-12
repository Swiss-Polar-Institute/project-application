from django.test import TestCase

from project_core.forms.scientific_clusters import ScientificClusterForm
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class ScientificClustersTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._keywords = database_population.create_keywords()
        self._academic_title = database_population.create_academic_title()
        self._gender = database_population.create_genders()[0]
        self._career_stage = database_population.create_career_stage()
        self._organisation_names = database_population.create_organisation_names()

    def test_create_scientific_cluster(self):
        prefix = 'SC'
        scientific_cluster_data = dict_to_multivalue_dict({
            f'{prefix}-title': 'Super Cluster',
            f'{prefix}-proposal': self._proposal,
            f'{prefix}-orcid': '0000-0002-1175-2668',
            f'{prefix}-first_name': 'John',
            f'{prefix}-email': 'john@example.org',
            f'{prefix}-surname': 'Doe',
            f'{prefix}-academic_title': self._academic_title,
            f'{prefix}-gender': self._gender,
            f'{prefix}-career_stage': self._career_stage,
            f'{prefix}-phone': '+12125552368',
            f'{prefix}-organisation_names': self._organisation_names[0]
        })

        scientific_cluster_data.setlist(f'{prefix}-keywords', self._keywords)

        scientific_cluster_form = ScientificClusterForm(data=scientific_cluster_data, prefix=prefix)
        self.assertTrue(scientific_cluster_form.is_valid())

        scientific_cluster = scientific_cluster_form.save()

        self.assertTrue(scientific_cluster.id)
        self.assertEqual(scientific_cluster.title, 'Super Cluster')
        self.assertEqual(scientific_cluster.sub_pi.person.first_name, 'John')
