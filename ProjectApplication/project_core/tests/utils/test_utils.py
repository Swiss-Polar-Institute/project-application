from django.test import TestCase

from project_core.utils.utils import bytes_to_human_readable


class UtilsUtilsTest(TestCase):
    def setUp(self):
        pass

    def test_bytes_to_human(self):
        self.assertEqual(bytes_to_human_readable(2048), '2.00 KB')
        self.assertEqual(bytes_to_human_readable(24545844), '23.41 MB')
