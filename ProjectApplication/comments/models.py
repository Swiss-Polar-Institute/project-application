from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

from project_core.models import CreateModify, Proposal, Call


# Models used by Proposal, Call...
class Category(CreateModify):
    category = models.CharField(max_length=100, help_text='Type of comment or attachment', unique=True)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = 'Categories'


class AbstractComment(CreateModify):
    text = models.TextField(help_text='Comment text', null=False,
                            blank=False)

    class Meta:
        unique_together = (('created_on', 'created_by'),)
        abstract = True


# Proposal
class ProposalCommentCategory(CreateModify):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.category

    class Meta:
        verbose_name_plural = 'Proposal Comment Categories'


class ProposalComment(AbstractComment):
    proposal = models.ForeignKey(Proposal, help_text='Proposal that this comment refers to',
                                 on_delete=models.PROTECT)
    category = models.ForeignKey(ProposalCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('proposal', 'created_on', 'created_by'),)


class ProposalAttachmentCategory(CreateModify):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.category

    class Meta:
        verbose_name_plural = 'Proposal Attachment Categories'


class ProposalAttachment(CreateModify):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to='attachments/proposals/')

    proposal = models.ForeignKey(Proposal, help_text='Proposal that this attachments belongs to',
                                 on_delete=models.PROTECT)
    category = models.ForeignKey(ProposalAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.proposal = parent

    @staticmethod
    def directory():
        return 'proposals'


# Call
class CallComment(AbstractComment):
    """Comments made about a call"""
    call = models.ForeignKey(Call, help_text='Call about which the comment was made', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('call', 'created_on', 'created_by'),)


class CallAttachmentCategory(CreateModify):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.category

    class Meta:
        verbose_name_plural = 'Call Attachment Categories'


class CallAttachment(CreateModify):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to='attachments/calls/')
    call = models.ForeignKey(Call, help_text='Call that this attachment belongs to',
                             on_delete=models.PROTECT)
    category = models.ForeignKey(CallAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)
