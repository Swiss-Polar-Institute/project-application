from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from project_core.fields import FlexibleDecimalField


class FlexibleNumberFieldTest(TestCase):
    def setUp(self):
        self._spi_number = FlexibleDecimalField()

    def _assert_equal_decimals(self, val1, val2):
        self.assertTrue(val1.compare(val2) == 0)

    def _assert_raises(self, val1):
        self.assertRaises(ValidationError, self._spi_number.clean, val1)
        # raise_error_if_orcid_invalid('0000-0002-1825-0098')


    def test_spi_number_field_valid_numbers(self):
        spi_number = self._spi_number

        self._assert_equal_decimals(spi_number.clean('1000'), Decimal('1000'))
        self._assert_equal_decimals(spi_number.clean('42.42'), Decimal('42.42'))
        self._assert_equal_decimals(spi_number.clean('-42.42'), Decimal('-42.42'))
        self._assert_equal_decimals(spi_number.clean('42,42'), Decimal('42.42'))
        self._assert_equal_decimals(spi_number.clean('-42,42'), Decimal('-42.42'))
        self._assert_equal_decimals(spi_number.clean('-1000.2'), Decimal('-1000.2'))
        self._assert_equal_decimals(spi_number.clean('-1000,2'), Decimal('-1000.2'))
        self._assert_equal_decimals(spi_number.clean("1'000"), Decimal('1000'))
        self._assert_equal_decimals(spi_number.clean("10'00"), Decimal('1000')) # single quotes are removed
        self._assert_equal_decimals(spi_number.clean("10'00"), Decimal('1000')) # single quotes are removed
        self._assert_equal_decimals(spi_number.clean("9‘000"), Decimal('9000')) # single quotes are removed

    def test_spi_number_field_invalid_numbers(self):
        # . and , are only decimal separators and we accept one or two decimals
        self._assert_raises('42,4200')
        self._assert_raises('42.4200')
        self._assert_raises('42.42.42')
        self._assert_raises('42.42,42')
        self._assert_raises('42,42,42')
        self._assert_raises('42.42.42')

