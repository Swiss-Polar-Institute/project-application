from datetime import datetime

from django.test import TestCase

from grant_management.forms.blog_posts import BlogPostModelForm
from grant_management.models import BlogPost
from project_core.tests import database_population


class BlogPostModelFormTest(TestCase):
    def setUp(self):
        self._project = database_population.create_project()

    def test_medium_valid(self):
        data = {'project': self._project,
                'due_date': datetime(2020, 1, 5),
                'received_date': datetime(2020, 5, 1),
                'title': 'The cold and the wind',
                'text': 'This is a blog post to explain that it was windy and cold',
                'author': self._project.principal_investigator.person,
                }

        self.assertEqual(BlogPost.objects.all().count(), 0)
        blog_post_form = BlogPostModelForm(data=data)
        self.assertTrue(blog_post_form.is_valid())
        blog_post_form.save()
        self.assertEqual(BlogPost.objects.all().count(), 1)
