from django.test import TestCase
from ....models import Call


class CallFormTest(TestCase):
    def setUp(self):
        pass

    def test_create_file_name(self):
        call = Call(long_name='Polar Access Fund 2020', short_name='PAF2020')
