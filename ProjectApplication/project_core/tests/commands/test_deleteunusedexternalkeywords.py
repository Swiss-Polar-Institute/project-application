from django.test import TestCase
from project_core.tests import database_population

class DeleteUnusedExternalKeywords(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._keywords = database_population.create_keywords()

    def test_xxx(self):
        print('Hello')

