from django.core.exceptions import ValidationError
from django.test import TestCase, SimpleTestCase

from project_core.widgets import CheckboxSelectMultipleSortable


class TestCheckboxSelectMultipleSortable(SimpleTestCase):
    def test_get_clean_order_ok(self):
        data = {'order': '1,2,3,4,5'}

        self.assertEqual(CheckboxSelectMultipleSortable.get_clean_order(data, 'order'), '1,2,3,4,5')

    def test_get_clean_order_missing(self):
        data = {}

        self.assertIsNone(CheckboxSelectMultipleSortable.get_clean_order(data, 'order'))

    def test_get_clean_order_validation_error(self):
        data = {'order': ',1,2,3,4'}

        self.assertRaises(ValidationError, CheckboxSelectMultipleSortable.get_clean_order, data, 'order')

    def test_get_clean_order_empty(self):
        data = {'order': ''}

        self.assertIsNone(CheckboxSelectMultipleSortable.get_clean_order(data, 'order'))
