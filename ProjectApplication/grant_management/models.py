from django.db import models
# Create your models here.
# add dates of review, signed date, who signed, grant agreement - need flexibilty in types of dates that are added
from storages.backends.s3boto3 import S3Boto3Storage

from project_core.models import CreateModifyOn, PhysicalPerson, Project


def grant_agreement_file_rename(instance, filename):
    return f'grant_management/GrantAgreement/Project-{instance.project.id}-{filename}'


class GrantAgreement(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project that this Grant Agreement belongs to',
                                on_delete=models.PROTECT)
    signed_date = models.DateField(help_text='Date that the grant agreement was signed', null=True, blank=True)
    signed_by = models.ForeignKey(PhysicalPerson, help_text='Person who signed the grant agreement', null=True,
                                  blank=True, on_delete=models.PROTECT)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=grant_agreement_file_rename)


class AbstractProjectReportDates(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Abstract containing dates',
                                on_delete=models.PROTECT)
    due_date = models.DateField(help_text='Date that the document is expected to be received', null=True, blank=True)
    sent_date = models.DateField(help_text='Date that the document was sent')
    reception_date = models.DateField(help_text='Date that the document was received')

    class Meta:
        abstract = True


def invoice_file_rename(instance, filename):
    return f'grant_management/Invoice/ProjectId-{instance.project.id}-{filename}'


class Invoice(AbstractProjectReportDates):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=invoice_file_rename, null=True, blank=True)
    paid_date = models.DateField(help_text='Date that the invoice was paid', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, help_text='Total of the invoice (CHF)', null=True,
                                 blank=True)


def finance_report_file_rename(instance, filename):
    return f'grant_management/FinanceReport/ProjectId-{instance.project.id}-{filename}'


class FinanceReport(AbstractProjectReportDates):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=finance_report_file_rename)
    sent_for_approval_date = models.DateField(help_text='Date that the finance report was sent for approval')
    signed_by = models.ForeignKey(PhysicalPerson, help_text='Person who signed the finance report',
                                  on_delete=models.PROTECT)


class LaySummary(AbstractProjectReportDates):
    text = models.TextField(help_text='Please enter summary here', null=False, blank=False)
    author = models.ForeignKey(PhysicalPerson, help_text='Person who entered this summary',
                               on_delete=models.PROTECT)
    web_version = models.TextField(help_text='Please the web version of the summary here', null=True, blank=True)


class License(CreateModifyOn):
    name = models.TextField(help_text='License name', null=False, blank=False)
    public_text = models.TextField(help_text='Explanatory text for this license', null=True, blank=True)


class Media(AbstractProjectReportDates):
    author = models.ForeignKey(PhysicalPerson, help_text='Person who entered this summary',
                               on_delete=models.PROTECT)
    license = models.ForeignKey(License, help_text='Type of license',
                                on_delete=models.PROTECT)
    copyright = models.TextField(help_text='Owner of copyright', null=True, blank=True)


class SocialNetwork(CreateModifyOn):
    name = models.TextField(help_text='Please enter social network title', null=False, blank=False)


class ProjectSocialMedia(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Choose related project',
                                on_delete=models.PROTECT)
    social_network = models.ForeignKey(SocialNetwork, help_text='Choose the related social network',
                                       on_delete=models.PROTECT)
    url = models.URLField(help_text='Web address of social media entry', null=True, blank=True)


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
