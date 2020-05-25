from django.test import TestCase

from ...templatetags.filename_from_path import short_filename_from_path, filename_from_path


class OrdinalTest(TestCase):
    def setUp(self):
        pass

    def short_filename_for_path_test(self):
        self.assertEqual(short_filename_from_path('directory/test.txt'), 'test.txt')
        self.assertEqual(short_filename_from_path('this/is/a/directory/This is a very long file name.pdf'),
                         'This is a ve…pdf')

    def filename_from_path_test(self):
        self.assertEqual(filename_from_path('a/b/name.txt'), 'name.txt')
