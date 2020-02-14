from django.test import TestCase

from project_core.tests import database_population
from ...forms.comment import CommentForm
from ...models import ProposalCommentCategory, Category, ProposalComment


class CommentFormTest(TestCase):
    def setUp(self):
        category, _ = Category.objects.get_or_create(name='Correspondence')
        self._proposal_comment_category, _ = ProposalCommentCategory.objects.get_or_create(category=category)
        self._proposal = database_population.create_proposal()

    def test_comment_submit(self):
        comment_form = CommentForm(category_queryset=ProposalCommentCategory.objects.all(),
                                   form_action='this-is-the-form-action')
        self.assertEqual(comment_form.helper['form_action'], 'this-is-the-form-action')

    def test_comment_save(self):
        self.assertEqual(ProposalComment.objects.all().count(), 0)

        post = {'category': self._proposal_comment_category.id,
                'text': 'This is a comment'}

        comment_form = CommentForm(post,
                                   category_queryset=ProposalCommentCategory.objects.all(),
                                   form_action='this-is-the-form-action')
        comment_form.is_valid()
        comment_form.save(self._proposal, None)

        self.assertEqual(ProposalComment.objects.all().count(), 1)
        proposal_comment_from_db = ProposalComment.objects.all()[0]

        self.assertEqual(proposal_comment_from_db.category, self._proposal_comment_category)
        self.assertEqual(proposal_comment_from_db.text, 'This is a comment')
