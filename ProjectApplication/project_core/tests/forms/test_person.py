from django.test import TestCase

from project_core.forms.person import PersonForm
from project_core.forms.scientific_clusters import ScientificClusterForm
from project_core.tests import database_population
from project_core.tests.utils_for_tests import dict_to_multivalue_dict


class PersonFormTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._keywords = database_population.create_keywords()
        self._academic_title = database_population.create_academic_title()
        self._gender = database_population.create_genders()[0]
        self._career_stage = database_population.create_career_stage()
        self._organisation_names = database_population.create_organisation_names()

    def test_create_person(self):

        person_form_data = dict_to_multivalue_dict({
            'orcid': '0000-0002-1175-2668',
            'first_name': 'John',
            'email': 'john@example.org',
            'surname': 'Doe',
            'academic_title': self._academic_title,
            'gender': self._gender,
            'career_stage': self._career_stage,
            'phone': '+12125552368',
            'organisation_names': self._organisation_names[0]
        })

        person_form = PersonForm(data=person_form_data)

        self.assertTrue(person_form.is_valid())

        person = person_form.save_person()

        self.assertTrue(person.id)
