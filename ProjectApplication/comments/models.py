from django.contrib.auth.models import User
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

from colours.models import ColourPair
from evaluation.models import ProposalEvaluation, CallEvaluation
from grant_management.models import Invoice, GrantAgreement
from project_core.models import CreateModifyOn, Proposal, Call, Project
# Models used by Proposal, Call...
from project_core.utils.utils import ProjectApplicationManagementFileValidator


class Category(CreateModifyOn):
    name = models.CharField(max_length=100, help_text='Type of comment or attachment', unique=True)
    colour = models.ForeignKey(ColourPair, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class AbstractComment(CreateModifyOn):
    text = models.TextField(help_text='Comment text', null=False,
                            blank=False)
    created_by = models.ForeignKey(User, help_text='User by which the entry was created',
                                   related_name="%(app_label)s_%(class)s_created_by_related", blank=True, null=True,
                                   on_delete=models.PROTECT)

    def truncate_text(self):
        max_text = 70
        if len(self.text) < max_text:
            text = self.text
        else:
            text = self.text[:max_text - 3] + '...'

        text = text.replace('\n', '\\n')
        return text

    class Meta:
        abstract = True


class AbstractAttachment(CreateModifyOn):
    text = models.TextField(help_text='Comment of the attachment', null=True, blank=True)
    created_by = models.ForeignKey(User, help_text='User by which the entry was created',
                                   related_name="%(app_label)s_%(class)s_created_by_related", blank=True, null=True,
                                   on_delete=models.PROTECT)

    class Meta:
        unique_together = (('created_on', 'created_by'),)
        abstract = True


# Proposal
class ProposalCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Proposal Comment Categories'


class ProposalComment(AbstractComment):
    proposal = models.ForeignKey(Proposal, help_text='Proposal that this comment refers to',
                                 on_delete=models.PROTECT)
    category = models.ForeignKey(ProposalCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, help_text='User by which the entry was created',
                                   related_name="%(app_label)s_%(class)s_created_by_related", blank=True, null=True,
                                   on_delete=models.PROTECT)

    def __str__(self):
        return f'Proposal:{self.proposal} Category:{self.category} Text: {self.truncate_text()}'

    def set_parent(self, parent):
        self.proposal = parent

    @staticmethod
    def category_queryset():
        return ProposalCommentCategory.objects.all()

    class Meta:
        unique_together = (('proposal', 'created_on', 'created_by'),)


class ProposalAttachmentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Proposal Attachment Categories'


def proposal_attachment_rename(instance, filename):
    return f'comments/ProposalAttachment/AttachmentProposal-{instance.proposal.id}-{filename}'


class ProposalAttachment(AbstractAttachment):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to=proposal_attachment_rename,
                            validators=[ProjectApplicationManagementFileValidator()])

    proposal = models.ForeignKey(Proposal, help_text='Proposal that this attachments belongs to',
                                 on_delete=models.PROTECT)
    category = models.ForeignKey(ProposalAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)

    def __str__(self):
        return f'Proposal:{self.proposal} Category:{self.category} File: {self.file.name}'

    def set_parent(self, parent):
        self.proposal = parent

    @staticmethod
    def category_queryset():
        return ProposalAttachmentCategory.objects.all()


# Call
class CallCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Call Comment Categories'


class CallComment(AbstractComment):
    """Comments made about a call"""
    call = models.ForeignKey(Call, help_text='Call about which the comment was made', on_delete=models.PROTECT)

    category = models.ForeignKey(CallCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    def __str__(self):
        return f'Call:{self.call} Category:{self.category} Text: {self.truncate_text()}'

    def set_parent(self, parent):
        self.call = parent

    @staticmethod
    def category_queryset():
        return CallCommentCategory.objects.all()

    class Meta:
        unique_together = (('call', 'created_on', 'created_by'),)


class CallAttachmentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Call Attachment Categories'


def call_attachment_rename(instance, filename):
    return f'comments/CallAttachment/AttachmentCall-{instance.call.id}-{filename}'


class CallAttachment(AbstractAttachment):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to=call_attachment_rename,
                            validators=[ProjectApplicationManagementFileValidator()])
    call = models.ForeignKey(Call, help_text='Call that this attachment belongs to',
                             on_delete=models.PROTECT)
    category = models.ForeignKey(CallAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)

    def __str__(self):
        return f'Call:{self.call.little_name()} Category:{self.category} File: {self.file.name}'

    def set_parent(self, parent):
        self.call = parent

    @staticmethod
    def category_queryset():
        return CallAttachmentCategory.objects.all()


# ProposalEvaluation
class ProposalEvaluationCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Proposal Evaluation Comment Categories'


class ProposalEvaluationComment(AbstractComment):
    """Comments made about a Proposal Evaluation"""
    proposal_evaluation = models.ForeignKey(ProposalEvaluation,
                                            help_text='Proposal Evaluation about which the comment was made',
                                            on_delete=models.PROTECT)

    category = models.ForeignKey(ProposalEvaluationCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.proposal_evaluation = parent

    @staticmethod
    def category_queryset():
        return ProposalEvaluationCommentCategory.objects.all()

    class Meta:
        unique_together = (('proposal_evaluation', 'created_on', 'created_by'),)


class ProposalEvaluationAttachmentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Proposal Evaluation Attachment Categories'


def proposal_evaluation_rename(instance, filename):
    return f'comments/ProposalEvaluationAttachment/AttachmentProposalEvaluation-{instance.proposal_evaluation.id}-{filename}'


class ProposalEvaluationAttachment(AbstractAttachment):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to=proposal_evaluation_rename,
                            validators=[ProjectApplicationManagementFileValidator()])
    proposal_evaluation = models.ForeignKey(ProposalEvaluation,
                                            help_text='Proposal Evaluation that this attachment belongs to',
                                            on_delete=models.PROTECT)
    category = models.ForeignKey(ProposalEvaluationAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.proposal_evaluation = parent

    @staticmethod
    def category_queryset():
        return ProposalEvaluationAttachmentCategory.objects.all()


# Project
class ProjectCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Project Comment Categories'


class ProjectComment(AbstractComment):
    """Comments made about a Proposal Evaluation"""
    project = models.ForeignKey(Project,
                                help_text='Project about which the comment was made',
                                on_delete=models.PROTECT)

    category = models.ForeignKey(ProjectCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.project = parent

    @staticmethod
    def category_queryset():
        return ProjectCommentCategory.objects.all()

    class Meta:
        unique_together = (('project', 'created_on', 'created_by'),)


class ProjectAttachmentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Project Attachment Categories'


def project_attachment_rename(instance, filename):
    return f'comments/ProjectAttachment/AttachmentProject-{instance.project.id}-{filename}'


class ProjectAttachment(AbstractAttachment):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to=project_attachment_rename,
                            validators=[ProjectApplicationManagementFileValidator()])
    project = models.ForeignKey(Project,
                                help_text='Project that this attachment belongs to',
                                on_delete=models.PROTECT)
    category = models.ForeignKey(ProjectAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.project = parent

    @staticmethod
    def category_queryset():
        return ProjectAttachmentCategory.objects.all()


# CallEvaluation
class CallEvaluationCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Call Evaluation Comment Categories'


class CallEvaluationComment(AbstractComment):
    """Comments made about a Proposal Evaluation"""
    call_evaluation = models.ForeignKey(CallEvaluation,
                                        help_text='Call Evaluation about which the comment was made',
                                        on_delete=models.PROTECT)

    category = models.ForeignKey(CallEvaluationCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    def __str__(self):
        return f'CallEvaluation:{self.call_evaluation} Category:{self.category} Text: {self.truncate_text()}'

    def set_parent(self, parent):
        self.call_evaluation = parent

    @staticmethod
    def category_queryset():
        return CallEvaluationCommentCategory.objects.all()

    class Meta:
        unique_together = (('call_evaluation', 'created_on', 'created_by'),)


# Invoice
class InvoiceCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Invoice Comment Categories'


class InvoiceComment(AbstractComment):
    """Comments made about a Proposal Evaluation"""
    invoice = models.ForeignKey(Invoice,
                                help_text='Call Evaluation about which the comment was made',
                                on_delete=models.PROTECT)

    category = models.ForeignKey(InvoiceCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    def __str__(self):
        return f'Invoice:{self.invoice} Category:{self.category} Text: {self.truncate_text()}'

    def set_parent(self, parent):
        self.invoice = parent

    @staticmethod
    def category_queryset():
        return InvoiceCommentCategory.objects.all()

    class Meta:
        unique_together = (('invoice', 'created_on', 'created_by'),)


# GrantAgreement
class GrantAgreementCommentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Grant Agreement Comment Categories'


class GrantAgreementComment(AbstractComment):
    """Comments made about a Proposal Evaluation"""
    grant_agreement = models.ForeignKey(GrantAgreement,
                                        help_text='GrantAgreement about which the comment was made',
                                        on_delete=models.PROTECT)

    category = models.ForeignKey(GrantAgreementCommentCategory, help_text='Type of comment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.grant_agreement = parent

    @staticmethod
    def category_queryset():
        return GrantAgreementCommentCategory.objects.all()

    class Meta:
        unique_together = (('grant_agreement', 'created_on', 'created_by'),)

    class Meta:
        verbose_name_plural = 'Grant Agreement Comments'


class GrantAgreementAttachmentCategory(CreateModifyOn):
    category = models.OneToOneField(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = 'Grant Agreement Attachment Categories'


def grant_agreement_attachment_rename(instance, filename):
    return f'comments/GrantAgreementAttachment/AttachmentGrantAgreement-{instance.grant_agreement.id}-{filename}'


class GrantAgreementAttachment(AbstractAttachment):
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to=grant_agreement_attachment_rename,
                            validators=[ProjectApplicationManagementFileValidator()])
    grant_agreement = models.ForeignKey(GrantAgreement,
                                        help_text='GrantAgreement that this attachment belongs to',
                                        on_delete=models.PROTECT)
    category = models.ForeignKey(GrantAgreementAttachmentCategory, help_text='Category of the attachment',
                                 on_delete=models.PROTECT)

    def set_parent(self, parent):
        self.grant_agreement = parent

    @staticmethod
    def category_queryset():
        return GrantAgreementAttachmentCategory.objects.all()

    class Meta:
        verbose_name_plural = 'Grant Agreement Attachments'
