from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from grant_management.models import GrantAgreement
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class ProjectListTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(reverse('logged-grant_management-project-list'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self._project.title)


class ProjectDetailsTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-project-detail', kwargs={'pk': self._project.id}))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self._project.title)


class ProjectBasicInformationUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-project-basic-information-update', kwargs={'pk': self._project.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        project_id = self._project.id

        self.assertEqual(self._project.start_date, date(2020, 1, 10))
        self.assertEqual(self._project.end_date, date(2022, 5, 7))

        data = MultiValueDict(
            {'start_date': ['10-05-2020'],
             'end_date': ['22-10-2020'],
             'save': ['Save Information']
             })

        response = self._client_management.post(
            reverse('logged-grant_management-project-basic-information-update', kwargs={'pk': project_id}),
            data=data
        )

        self.assertEqual(response.status_code, 302)
        self._project.refresh_from_db()

        self.assertEqual(self._project.start_date, date(2020, 5, 10))
        self.assertEqual(self._project.end_date, date(2020, 10, 22))


class GrantAgreementAddViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-grant_agreement-add', kwargs={'project': self._project.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        project_id = self._project.id
        signed_by_id = self._project.principal_investigator.person.id

        self.assertFalse(hasattr(self._project, 'grantagreement'))

        data = MultiValueDict(
            {'project': [str(project_id)],
             'signed_by': [str(signed_by_id)],
             'signed_date': ['01-05-2020'],
             'file': [SimpleUploadedFile('grant_agreement.txt',
                                         b'This is the signed grant agreement. C.')]
             })

        response = self._client_management.post(
            reverse('logged-grant_management-grant_agreement-add', kwargs={'project': project_id}),
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self._project.refresh_from_db()

        self.assertTrue(hasattr(self._project, 'grantagreement'))
        grant_agreement = self._project.grantagreement

        self.assertEqual(grant_agreement.signed_date, date(2020, 5, 1))
        self.assertEqual(list(grant_agreement.signed_by.all()), [self._project.principal_investigator.person])
        self.assertTrue(grant_agreement.file.name != '')


class ProjectUpdateTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-project-update', kwargs={'pk': self._project.id})
        )
        self.assertEqual(response.status_code, 200)


class GrantAgreementUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        grant_agreement = GrantAgreement(project=self._project)
        grant_agreement.save()

        response = self._client_management.get(
            reverse('logged-grant_management-grant_agreement-update', kwargs={'pk': self._project.grantagreement.id})
        )
        self.assertEqual(response.status_code, 200)


class LaySummariesRawTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_get(self):
        c = Client()
        response = c.get(reverse('lay-summaries-raw', kwargs={'call': self._project.call.id}))
        self.assertEqual(response.status_code, 200)


class BlogPostsUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-blog_posts-update', kwargs={'project': self._project.id})
        )
        self.assertEqual(response.status_code, 200)


class InstallmentsUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-installments-update', kwargs={'project': self._project.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = dict_to_multivalue_dict({'FORM_SET-TOTAL_FORMS': 1,
                                        'FORM_SET-INITIAL_FORMS': 1,
                                        'FORM_SET-MIN_NUM_FORMS': 1,
                                        'FORM_SET-MAX_NUM_FORMS': 1000,
                                        'FORM_SET-0-project': self._project.id,
                                        'FORM_SET-0-id': 6,
                                        'FORM_SET-0-DELETE': '',
                                        'FORM_SET-0-can_be_deleted': 0,
                                        'FORM_SET-0-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-0-amount': 50
                                        })

        response = self._client_management.post(
            reverse('logged-grant_management-installments-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 200)
