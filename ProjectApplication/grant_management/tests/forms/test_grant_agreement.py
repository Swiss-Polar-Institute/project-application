from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ProjectApplication import settings
from grant_management.forms.grant_agreement import GrantAgreementForm
from grant_management.models import GrantAgreement
from project_core.models import PhysicalPerson
from project_core.tests import database_population


class GrantAgreementFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_grant_agreement_valid(self):
        data = {'project': self._project,
                'signed_date': datetime(2020, 1, 10),
                'signed_by': PhysicalPerson.objects.filter(id=self._project.principal_investigator.person.id)
                }
        files = {'file': SimpleUploadedFile('grant_agreement.pdf',
                                            b'This is the signed grant agreement. C.')
                 }

        self.assertEqual(GrantAgreement.objects.all().count(), 0)
        grant_agreement_form = GrantAgreementForm(data=data, files=files, project=self._project)
        self.assertTrue(grant_agreement_form.is_valid())
        grant_agreement_form.save()
        self.assertEqual(GrantAgreement.objects.all().count(), 1)
