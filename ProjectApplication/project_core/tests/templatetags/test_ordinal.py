from django.test import TestCase

from ...templatetags.ordinal import ordinal


class OrdinalTest(TestCase):
    def setUp(self):
        pass

    def test_ordinal(self):
        self.assertEqual(ordinal(1), 'First')
        self.assertEqual(ordinal(2), 'Second')
        self.assertEqual(ordinal(11), '11th')
        self.assertEqual(ordinal(None), None)
