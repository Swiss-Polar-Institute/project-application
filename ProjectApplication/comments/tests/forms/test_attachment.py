from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# dependencies of project_core could be removed - but this way is doing integration test
# as well. This can be refactored
from project_core.tests import database_population
from ...forms.attachment import AttachmentForm
from ...models import ProposalCommentCategory, Category, ProposalAttachment, ProposalAttachmentCategory


class AttachmentFormTest(TestCase):
    def setUp(self):
        category, _ = Category.objects.get_or_create(name='Correspondence')
        self._proposal_attachment_category, _ = ProposalAttachmentCategory.objects.get_or_create(category=category)
        self._proposal = database_population.create_proposal()

    def test_attachment_submit(self):
        attachment_form = AttachmentForm(category_queryset=ProposalCommentCategory.objects.all(),
                                         form_action='this-is-the-form-action')
        self.assertEqual(attachment_form.helper['form_action'], 'this-is-the-form-action')

    def test_attachment_save(self):
        self.assertEqual(ProposalAttachment.objects.all().count(), 0)

        post = {f'{AttachmentForm.FORM_NAME}-category': self._proposal_attachment_category.id,
                f'{AttachmentForm.FORM_NAME}-text': 'This is a comment',
                }

        files = {f'{AttachmentForm.FORM_NAME}-file': SimpleUploadedFile('correspondence.pdf',
                                                                        b'This is an email received. C.')}

        attachment_form = AttachmentForm(post,
                                         files,
                                         category_queryset=ProposalAttachmentCategory.objects.all(),
                                         form_action='this-is-the-form-action',
                                         prefix=AttachmentForm.FORM_NAME)

        self.assertTrue(attachment_form.is_valid())
        attachment_form.save(self._proposal, None)

        self.assertEqual(ProposalAttachment.objects.all().count(), 1)
        proposal_attachment_from_db = ProposalAttachment.objects.all()[0]

        self.assertEqual(proposal_attachment_from_db.category, self._proposal_attachment_category)
        self.assertEqual(proposal_attachment_from_db.text, 'This is a comment')
