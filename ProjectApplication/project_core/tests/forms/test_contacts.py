from django.test import TestCase

from project_core.forms.contacts import ContactForm
from project_core.models import PersonPosition
from project_core.tests import database_population


class ContactFormTest(TestCase):
    def setUp(self):
        self._academic_title = database_population.create_academic_title()
        self._gender = database_population.create_genders()[0]
        self._organisations = database_population.create_organisation_names()

    def test_contact_valid(self):
        data = {'academic_title': self._academic_title.id,
                'group': 'IT and data',
                'organisation_names': self._organisations,
                'person__gender': self._gender,
                'person__first_name': 'John',
                'person__surname': 'Doe',
                'privacy_policy': True,
                }
        contact_form = ContactForm(data)

        self.assertEqual(PersonPosition.objects.all().count(), 0)
        self.assertTrue(contact_form.is_valid())

        contact_form.save()

        self.assertEqual(PersonPosition.objects.all().count(), 1)

        person_position = PersonPosition.objects.all()[0]

        self.assertEqual(person_position.academic_title, self._academic_title)
        self.assertEqual(person_position.group, 'IT and data')
        self.assertEqual(person_position.person.gender, self._gender)
        self.assertEqual(person_position.person.first_name, 'John')
        self.assertEqual(person_position.person.surname, 'Doe')
