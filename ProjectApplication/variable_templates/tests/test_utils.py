from django.test import TestCase

from project_core.tests import database_population as project_core_database_population
from . import database_population
from .. import utils


class UtilsTest(TestCase):
    def setUp(self):
        self._call = project_core_database_population.create_call()
        database_population.create_default_variables()

    def test_get_template_value(self):
        utils.get_template_value('activity', self._call)
