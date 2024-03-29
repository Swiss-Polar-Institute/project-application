from django.http import HttpRequest
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from evaluation.models import Reviewer
from ... import database_population
from ....models import Proposal
from ....views.logged import proposal


class ManagementProposalTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()

        self._proposal = database_population.create_proposal()
        self._proposal.eligibility = Proposal.ELIGIBLE
        self._proposal.save()

        self._management_user = database_population.create_management_user()
        self._reviewer_user = database_population.create_reviewer_user()

        self._client_management = database_population.create_management_logged_client()

    def test_create_file_name(self):
        filename = proposal.create_file_name('this-is-{}-something-{}.csv', self._call.id)
        self.assertRegex(filename, '^this-is-GLACE_2018-something-[0-9]{8}-[0-9]{6}\.csv$')

        self._call.short_name = 'GLACE'
        self._call.save()
        filename = proposal.create_file_name('this-is-{}-something-{}.csv', self._call.id)
        self.assertRegex(filename, '^this-is-GLACE-something-[0-9]{8}-[0-9]{6}\.csv$')

    def test_propsoals_export_csv_summary_for_a_specific_call(self):
        call_no_proposals = database_population.create_call_long_name('This is a call without proposals',
                                                                      'no proposals 2020')

        response = self._client_management.get(
            reverse('logged-export-proposals-csv-summary-call', args=[call_no_proposals.id]))

        # Checks that only one line is in the response: the header
        self.assertEqual(response.content.decode('utf-8').count('\n'), 1)

    def test_proposals_export_csv_summary(self):
        response = self._client_management.get(
            reverse('logged-export-proposals-csv-summary-call', args=[str(self._proposal.call.id)]))

        self.assertContains(response, 'A test proposal')

    def test_proposals_export_csv_summary_reviewer_no_access(self):
        c = Client()

        reviewer = Reviewer(user=self._reviewer_user)
        reviewer.save()
        reviewer.calls.remove(self._proposal.call)
        reviewer.save()

        login = c.login(username='unittest_reviewer', password='12345', request=HttpRequest())
        self.assertTrue(login)

        response = c.get(
            reverse('logged-export-proposals-csv-summary-call', args=[str(self._proposal.call.id)]))

        self.assertNotContains(response, 'A test proposal')

    def test_proposals_export_csv_summary_reviewer_access(self):
        c = Client()

        reviewer = Reviewer(user=self._reviewer_user)
        reviewer.save()
        reviewer.calls.add(self._proposal.call)
        reviewer.save()

        login = c.login(username='unittest_reviewer', password='12345', request=HttpRequest())
        self.assertTrue(login)

        response = c.get(
            reverse('logged-export-proposals-csv-summary-call', args=[str(self._proposal.call.id)]))

        self.assertContains(response, 'A test proposal')

    def test_load_logged_proposal_list(self):
        response = self._client_management.get(reverse('logged-proposal-list'))

        self.assertEqual(response.status_code, 200)

    def test_export_to_excel(self):
        response = self._client_management.get(
            reverse('logged-export-proposals-for-call-excel', kwargs={'call': self._call.id}))

        self.assertEqual(response.status_code, 200)
