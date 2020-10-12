import json
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from ProjectApplication import settings
from grant_management.models import GrantAgreement, Installment, Invoice, LaySummaryType, LaySummary
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
            reverse('logged-grant_management-project-basic-information-update', kwargs={'project': self._project.id})
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
            reverse('logged-grant_management-project-basic-information-update', kwargs={'project': project_id}),
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
             'file': [SimpleUploadedFile('grant_agreement.pdf',
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
        response = c.get(reverse('lay-summaries-for_website', kwargs={'call': self._project.call.id}))
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

    def test_post_valid(self):
        data = dict_to_multivalue_dict({'FORM_SET-TOTAL_FORMS': 1,
                                        'FORM_SET-INITIAL_FORMS': 0,
                                        'FORM_SET-MIN_NUM_FORMS': 1,
                                        'FORM_SET-MAX_NUM_FORMS': 1000,
                                        'FORM_SET-0-project': self._project.id,
                                        'FORM_SET-0-id': '',
                                        'FORM_SET-0-DELETE': '',
                                        'FORM_SET-0-can_be_deleted': 0,
                                        'FORM_SET-0-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-0-amount': 50
                                        })

        self.assertEqual(Installment.objects.all().count(), 0)
        response = self._client_management.post(
            reverse('logged-grant_management-installments-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Installment.objects.all().count(), 1)

    def test_post_invalid(self):
        data = dict_to_multivalue_dict({'FORM_SET-TOTAL_FORMS': 2,
                                        'FORM_SET-INITIAL_FORMS': 0,
                                        'FORM_SET-MIN_NUM_FORMS': 1,
                                        'FORM_SET-MAX_NUM_FORMS': 1000,
                                        'FORM_SET-0-project': self._project.id,
                                        'FORM_SET-0-id': '',
                                        'FORM_SET-0-DELETE': '',
                                        'FORM_SET-0-can_be_deleted': 0,
                                        'FORM_SET-0-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-0-amount': 15_000,
                                        'FORM_SET-1-project': self._project.id,
                                        'FORM_SET-1-id': '',
                                        'FORM_SET-1-DELETE': '',
                                        'FORM_SET-1-can_be_deleted': 0,
                                        'FORM_SET-1-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-1-amount': 10_000
                                        })

        self.assertEqual(Installment.objects.all().count(), 0)
        response = self._client_management.post(
            reverse('logged-grant_management-installments-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Installment.objects.all().count(), 0)
        self.assertEqual(list(response.context['messages'])[0].message,
                         'Installments not saved. Verify errors in the form')


class InvoicesUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-invoices-update', kwargs={'project': self._project.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # Lay Summary Type needs to exist because during the invoice checking it does
        # a lookup for the settings.LAY_SUMMARY_ORIGINAL
        lay_summary_type = LaySummaryType.objects.create(name=settings.LAY_SUMMARY_ORIGINAL,
                                                         description='Original')

        installment = Installment.objects.create(project=self._project,
                                                 amount=500)

        data = dict_to_multivalue_dict({'FORM_SET-TOTAL_FORMS': 1,
                                        'FORM_SET-INITIAL_FORMS': 0,
                                        'FORM_SET-MIN_NUM_FORMS': 1,
                                        'FORM_SET-MAX_NUM_FORMS': 1000,
                                        'FORM_SET-0-project': self._project.id,
                                        'FORM_SET-0-id': '',
                                        'FORM_SET-0-DELETE': '',
                                        'FORM_SET-0-can_be_deleted': 0,
                                        'FORM_SET-0-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-0-amount': 50,
                                        'FORM_SET-0-installment': installment.id
                                        })

        self.assertEqual(Invoice.objects.all().count(), 0)
        response = self._client_management.post(
            reverse('logged-grant_management-invoices-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Invoice.objects.all().count(), 1)

    def _data_two_invoices(self, installment, amount):
        return dict_to_multivalue_dict({'FORM_SET-TOTAL_FORMS': 2,
                                        'FORM_SET-INITIAL_FORMS': 0,
                                        'FORM_SET-MIN_NUM_FORMS': 1,
                                        'FORM_SET-MAX_NUM_FORMS': 1000,
                                        'FORM_SET-0-project': self._project.id,
                                        'FORM_SET-0-id': '',
                                        'FORM_SET-0-DELETE': '',
                                        'FORM_SET-0-can_be_deleted': 0,
                                        'FORM_SET-0-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-0-amount': 12_000,
                                        'FORM_SET-0-installment': installment.id,
                                        'FORM_SET-1-project': self._project.id,
                                        'FORM_SET-1-id': '',
                                        'FORM_SET-1-DELETE': '',
                                        'FORM_SET-1-can_be_deleted': 0,
                                        'FORM_SET-1-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-1-amount': 12_000,
                                        'FORM_SET-1-installment': installment.id,
                                        })

    def test_post_invoices_too_big(self):
        lay_summary_type = LaySummaryType.objects.create(name=settings.LAY_SUMMARY_ORIGINAL,
                                                         description='Original')

        installment = Installment.objects.create(project=self._project,
                                                 amount=20_000)

        data = self._data_two_invoices(installment, 12_000)

        self.assertEqual(Invoice.objects.all().count(), 0)
        response = self._client_management.post(
            reverse('logged-grant_management-invoices-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Save Force Going Overbudget')
        self.assertEqual(Invoice.objects.all().count(), 0)

    def test_post_invoices_too_big_force(self):
        lay_summary_type = LaySummaryType.objects.create(name=settings.LAY_SUMMARY_ORIGINAL,
                                                         description='Original')

        installment = Installment.objects.create(project=self._project,
                                                 amount=20_000)

        data = self._data_two_invoices(installment, 12_000)
        data['save_force'] = 'Save Force Going Overbudget'

        self.assertEqual(Invoice.objects.all().count(), 0)
        response = self._client_management.post(
            reverse('logged-grant_management-invoices-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Invoice.objects.all().count(), 2)


class LaySummariesUpdateViewTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client_management = database_population.create_management_logged_client()

    def test_get(self):
        response = self._client_management.get(
            reverse('logged-grant_management-lay_summaries-update', kwargs={'project': self._project.id})
        )

        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # Lay Summary Type needs to exist because during the invoice checking it does
        # a lookup for the settings.LAY_SUMMARY_ORIGINAL
        lay_summary_type = LaySummaryType.objects.create(name=settings.LAY_SUMMARY_ORIGINAL,
                                                         description='Original')

        data = dict_to_multivalue_dict({'FORM_SET-TOTAL_FORMS': 1,
                                        'FORM_SET-INITIAL_FORMS': 0,
                                        'FORM_SET-MIN_NUM_FORMS': 1,
                                        'FORM_SET-MAX_NUM_FORMS': 1000,
                                        'FORM_SET-0-project': self._project.id,
                                        'FORM_SET-0-id': '',
                                        'FORM_SET-0-DELETE': '',
                                        'FORM_SET-0-can_be_deleted': 0,
                                        'FORM_SET-0-due_date': date(2020, 5, 14).strftime('%d-%m-%Y'),
                                        'FORM_SET-0-lay_summary_type': lay_summary_type.id
                                        })

        self.assertEqual(LaySummary.objects.all().count(), 0)
        response = self._client_management.post(
            reverse('logged-grant_management-lay_summaries-update', kwargs={'project': self._project.id}),
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LaySummary.objects.all().count(), 1)


class TestApiListMediaView(TestCase):
    def setUp(self):
        self._project = database_population.create_project()
        self._client = Client()

    def test_get_no_api_key(self):
        response = self._client.get(
            f'{reverse("api-list-media-view")}?modified_since=2017-01-28T21:00:00+00:00'
        )

        self.assertContains(response, '"ApiKey" HTTP header is required', status_code=400)

    def test_get_invalid_api_key(self):
        response = self._client.get(
            f'{reverse("api-list-media-view")}?modified_since=2017-01-28T21:00:00+00:00',
            HTTP_ApiKey='test'
        )

        self.assertContains(response, 'Received ApiKey header (test) does not match settings.API_SECRET_KEY',
                            status_code=403)

    def test_get_media_empty(self):
        response = self._client.get(
            f'{reverse("api-list-media-view")}?modified_since=2017-01-28T21:00:00+00:00',
            HTTP_ApiKey=settings.API_SECRET_KEY
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[]')

    def test_get_one_medium(self):
        project = database_population.create_project()
        medium = database_population.create_medium(project)

        response = self._client.get(
            f'{reverse("api-list-media-view")}?modified_since=2017-01-28T21:00:00+00:00',
            HTTP_ApiKey=settings.API_SECRET_KEY
        )

        self.assertEqual(response.status_code, 200)

        json_body = json.loads(response.content)

        self.assertEqual(len(json_body), 1)

        medium_json = json_body[0]

        self.assertEqual(medium_json['license'], None)
        self.assertEqual(medium_json['copyright'], medium.copyright)
        self.assertEqual(medium_json['file_md5'], medium.file_md5)
        self.assertEqual(medium_json['descriptive_text'], medium.descriptive_text)
