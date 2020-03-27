from django.core.exceptions import ValidationError
from django.test import TestCase

from project_core.utils.orcid import raise_error_if_orcid_invalid


class UtilsOrcidTest(TestCase):
    def setUp(self):
        pass

    def test_orcid_is_valid(self):
        self.assertRaises(ValidationError, raise_error_if_orcid_invalid, '0000-0002-1825-0097')
        raise_error_if_orcid_invalid('0000-0002-1825-0098')
