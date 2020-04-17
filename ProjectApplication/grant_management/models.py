from django.db import models
# Create your models here.
# add dates of review, signed date, who signed, grant agreement - need flexibilty in types of dates that are added
from storages.backends.s3boto3 import S3Boto3Storage

from project_core.models import CreateModifyOn, PhysicalPerson, Project


def grant_agreement_file_rename(instance, filename):
    return f'grant_management/GrantAgreement/Project-{instance.project.id}-{filename}'


class GrantAgreement(CreateModifyOn):
    project = models.OneToOneField(Project, help_text='Project this Grant Agreement belongs to',
                                   on_delete=models.PROTECT)
    signed_date = models.DateField(help_text='Date the grant agreement was signed', null=True, blank=True)
    signed_by = models.ForeignKey(PhysicalPerson, help_text='Person who signed the grant agreement', null=True,
                                  blank=True, on_delete=models.PROTECT)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=grant_agreement_file_rename)

    def __str__(self):
        return f'{self.project}'


class AbstractProjectReportDates(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Abstract containing dates',
                                on_delete=models.PROTECT)
    due_date = models.DateField(help_text='Date the document is expected to be received')
    sent_date = models.DateField(help_text='Date the document was sent', null=True, blank=True)
    reception_date = models.DateField(help_text='Date the document was received', null=True, blank=True)

    def __str__(self):
        return f'{self.project}'

    class Meta:
        abstract = True


def invoice_file_rename(instance, filename):
    return f'grant_management/Invoice/ProjectId-{instance.project.id}-{filename}'


class Invoice(AbstractProjectReportDates):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=invoice_file_rename, null=True, blank=True)
    paid_date = models.DateField(help_text='Date the invoice was paid', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, help_text='Total of the invoice (CHF)', null=True,
                                 blank=True)

    def __str__(self):
        return f'Id: {self.id} Amount: {self.amount}'


def finance_report_file_rename(instance, filename):
    return f'grant_management/FinanceReport/ProjectId-{instance.project.id}-{filename}'


class FinancialReport(AbstractProjectReportDates):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=finance_report_file_rename, blank=True, null=True)
    approval_date = models.DateField(help_text='Date the finance report was approved',
                                     blank=True, null=True)
    approved_by = models.ForeignKey(PhysicalPerson, help_text='Person who signed the finance report',
                                    on_delete=models.PROTECT, blank=True, null=True)


class LaySummary(AbstractProjectReportDates):
    text = models.TextField(help_text='Please enter summary here', null=False, blank=False)
    author = models.ForeignKey(PhysicalPerson, help_text='Person who entered this summary',
                               on_delete=models.PROTECT)
    web_version = models.TextField(help_text='Please the web version of the summary here', null=True, blank=True)

    def __str__(self):
        return f'{self.text[:20]}'


class License(CreateModifyOn):
    name = models.TextField(help_text='License name', null=False, blank=False)
    public_text = models.TextField(help_text='Explanatory text for this license', null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Media(AbstractProjectReportDates):
    author = models.ForeignKey(PhysicalPerson, help_text='Person who entered this summary',
                               on_delete=models.PROTECT)
    license = models.ForeignKey(License, help_text='Type of license',
                                on_delete=models.PROTECT)
    copyright = models.TextField(help_text='Owner of copyright', null=True, blank=True)

    # TODO: add file to the media?

    def __str__(self):
        return f'{self.project}-{self.author}'


class SocialNetwork(CreateModifyOn):
    name = models.TextField(help_text='Please enter social network title', null=False, blank=False)

    def __str__(self):
        return f'{self.name}'


class ProjectSocialMedia(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Choose related project',
                                on_delete=models.PROTECT)
    social_network = models.ForeignKey(SocialNetwork, help_text='Choose the related social network',
                                       on_delete=models.PROTECT)
    url = models.URLField(help_text='Web address of social media entry', null=True, blank=True)

    def __str__(self):
        return f'{self.project}-{self.social_network}'


class Publication(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Choose related project',
                                on_delete=models.PROTECT)
    doi = models.TextField(help_text='DOI reference for entry', null=True, blank=True)
    reference = models.TextField(help_text='Journal reference for entry', null=True, blank=True)
    title = models.TextField(help_text='Publication title', null=False, blank=False)
    date_time_published = models.DateTimeField(help_text='Date of the publication', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.title)


class Dataset(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Choose related project',
                                on_delete=models.PROTECT)
    doi = models.TextField(help_text='DOI reference for entry', null=True, blank=True)
    url = models.URLField(help_text='Web address for entry', null=True, blank=True)
    title = models.TextField(help_text='Dataset title', null=False, blank=False)
    date_published = models.DateField(help_text='Date of publication', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.title)
