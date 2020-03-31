from django.test import TestCase
from django.urls import reverse

from project_core.tests import database_population
from .. import utils
from ..forms.attachment import AttachmentForm
from ..forms.comment import CommentForm
from ..models import Category, ProposalCommentCategory, ProposalComment


class UtilsTest(TestCase):
    def setUp(self):
        self._proposal = database_population.create_proposal()
        self._category, _ = Category.objects.get_or_create(name='Budget')
        self._proposal_comment_category, _ = ProposalCommentCategory.objects.get_or_create(category=self._category)

        self._user_management = database_population.create_management_logged_client()

    def test_add_comment_attachment_forms(self):
        context = {}
        submit_viewname = 'logged-proposal-comment-add'
        parent = self._proposal

        context.update(utils.comments_attachments_forms(submit_viewname, parent))

        self.assertIn('comments', context)
        self.assertIn('attachments', context)
        self.assertIn(CommentForm.FORM_NAME, context)
        self.assertIn(AttachmentForm.FORM_NAME, context)

    def test_process_comment_success(self):
        parent = self._proposal
        submit_viewname_repost = 'logged-proposal-comment-add'

        self.assertEqual(ProposalComment.objects.all().count(), 0)

        comment_text = 'This is a very good comment'

        self._user_management.post(reverse(submit_viewname_repost, kwargs={'pk': parent.id}),
                                   data={'comment_form_submit': '1',
                                         f'{CommentForm.FORM_NAME}-category': self._proposal_comment_category.id,
                                         f'{CommentForm.FORM_NAME}-text': comment_text}
                                   , follow=True)

        self.assertEqual(ProposalComment.objects.all().count(), 1)
        proposal_comment = ProposalComment.objects.all().first()
        self.assertEqual(proposal_comment.text, comment_text)
        self.assertEqual(proposal_comment.category, self._proposal_comment_category)

    def test_process_comment_success_failure(self):
        parent = self._proposal
        url = reverse('logged-proposal-comment-add', kwargs={'pk': parent.id})

        self.assertEqual(ProposalComment.objects.all().count(), 0)

        comment_text = ''

        response = self._user_management.post(url,
                                              data={'comment_form_submit': '1',
                                                    f'{CommentForm.FORM_NAME}-category': self._proposal_comment_category.id,
                                                    f'{CommentForm.FORM_NAME}-text': comment_text}
                                              )

        self.assertEqual(ProposalComment.objects.all().count(), 0)

        message_text = list(response.context['messages'])[0].message

        self.assertEqual(message_text,
                         'Error saving the comment. Check the information in the comments section.')
