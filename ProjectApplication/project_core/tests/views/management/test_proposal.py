from django.test import TestCase

from ... import database_population
from ....views.management import proposal


class CallFormTest(TestCase):
    def setUp(self):
        self._call = database_population.create_call()

    def test_create_file_name(self):
        filename = proposal.create_file_name('this-is-{}-something-{}.csv', self._call.id)
        self.assertRegex(filename, '^this-is-GreenLAnd_Circumnavigation_Expedition-something-[0-9]{8}-[0-9]{6}\.csv$')

        self._call.short_name = 'GLACE'
        self._call.save()
        filename = proposal.create_file_name('this-is-{}-something-{}.csv', self._call.id)
        self.assertRegex(filename, '^this-is-GLACE-[0-9]{8}-[0-9]{6}\.csv$')
