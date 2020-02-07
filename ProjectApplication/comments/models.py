from django.db import models

from project_core.models import CreateModify, Proposal, Call


class AbstractComment(CreateModify):
    text = models.TextField(help_text='Comment text', null=False,
                            blank=False)

    class Meta:
        unique_together = (('created_on', 'created_by'),)
        abstract = True


class ProposalComment(AbstractComment):
    proposal = models.ForeignKey(Proposal, help_text='Proposal that this comment refers to',
                                 on_delete=models.PROTECT, )

    class Meta:
        unique_together = (('proposal', 'created_on', 'created_by'),)


class CallComment(AbstractComment):
    """Comments made about a call"""
    call = models.ForeignKey(Call, help_text='Call about which the comment was made', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('call', 'created_on', 'created_by'),)
