from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population


class ProposalsExportZip(StaticLiveServerTestCase):
    port = 9998

    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._client_management = database_population.create_management_logged_client()

    def test_get_ok(self):
        response = self._client_management.get(
            reverse('proposal-detail-zip',
                    kwargs={'uuid': self._proposal.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['content-disposition'].endswith('.zip"'))
        self.assertTrue(response['content-disposition'].startswith('attachment; filename="'))
        self.assertGreaterEqual(int(response['content-length']), 98000)
