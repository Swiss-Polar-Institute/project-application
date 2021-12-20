from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class OrganisationsAutocompleteTest(StaticLiveServerTestCase):
    port = 9998

    def setUp(self):
        self._proposal = database_population.create_proposal()

    def test_get(self):
        client = Client()

        response = client.get(reverse('proposal-detail-zip',
                                      kwargs={'uuid': self._proposal.uuid})
                              )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/zip')
        self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename="GLACE_2018-John_Smith.zip"')
        self.assertGreaterEqual(int(response.headers['Content-Length']), 98000)
        self.assertTrue(response.content.startswith(b'PK'))
