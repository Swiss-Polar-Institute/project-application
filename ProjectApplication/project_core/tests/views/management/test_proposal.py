from django.test import Client
from django.test import TestCase
from django.urls import reverse

from ... import database_population
from ....views.management import proposal


class ManagementProposalTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()
        self._proposal = database_population.create_proposal()
        database_population.create_management_user()

    def test_create_file_name(self):
        filename = proposal.create_file_name('this-is-{}-something-{}.csv', self._call.id)
        self.assertRegex(filename, '^this-is-GreenLAnd_Circumnavigation_Expedition-something-[0-9]{8}-[0-9]{6}\.csv$')

        self._call.short_name = 'GLACE'
        self._call.save()
        filename = proposal.create_file_name('this-is-{}-something-{}.csv', self._call.id)
        self.assertRegex(filename, '^this-is-GLACE-something-[0-9]{8}-[0-9]{6}\.csv$')

    def test_proposals_export_csv_summary(self):
        c = Client()

        login = c.login(username='unittest', password='12345')
        self.assertTrue(login)

        response = c.get(
            reverse('management-export-proposals-csv-summary-call', args=[str(self._proposal.call.id)]))

        self.assertContains(response, 'A test proposal')
