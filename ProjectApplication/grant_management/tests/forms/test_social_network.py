from django.test import TestCase

from grant_management.forms.social_network import SocialNetworkModelForm
from grant_management.models import SocialNetwork, ProjectSocialNetwork
from project_core.tests import database_population


class SocialNetworkModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_medium_valid(self):
        social_network, _ = SocialNetwork.objects.get_or_create(name='Twitter')

        data = {'project': self._project,
                'social_network': social_network,
                'url': 'https://www.twitter.com/AProject',
                }

        self.assertEqual(ProjectSocialNetwork.objects.all().count(), 0)
        social_network_form = SocialNetworkModelForm(data=data)
        self.assertTrue(social_network_form.is_valid())
        social_network_form.save()
        self.assertEqual(ProjectSocialNetwork.objects.all().count(), 1)
