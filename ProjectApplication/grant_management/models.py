import os

from django.db import models
# Create your models here.
# add dates of review, signed date, who signed, grant agreement - need flexibilty in types of dates that are added
from storages.backends.s3boto3 import S3Boto3Storage

from project_core.models import CreateModifyOn, PhysicalPerson, Project


def grant_agreement_file_rename(instance, filename):
    upload_to = 'grant_management/grant_agreement'

    filename = f'GrantAgreement-{instance.id}-ProjectId-{instance.project.id}-{filename}'

    return os.path.join(upload_to, filename)


class GrantAgreement(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project that this Grant Agreement belongs to',
                                on_delete=models.PROTECT)
    signed_date = models.DateField(help_text='Date that the grant agreement was signed', null=True, blank=True)
    signed_by = models.ForeignKey(PhysicalPerson, help_text='Person who signed the grant agreement', null=True,
                                  blank=True)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=grant_agreement_file_rename)


def invoice_file_rename(instance, filename):
    upload_to = 'invoice/invoice'

    filename = f'Invoice-{instance.id}-ProjectId-{instance.project.id}-{filename}'

    return os.path.join(upload_to, filename)


class Invoice(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project that this invoice originates from',
                                on_delete=models.PROTECT)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=invoice_file_rename, null=True, blank=True)
    due_date = models.DateField(help_text='Date that the invoice was signed')
    sent_date = models.DateField(help_text='Date that the invoice was sent', null=True, blank=True)
    reception_date = models.DateField(help_text='Date that the invoice was received', null=True, blank=True)
    paid_date = models.DateField(help_text='Date that the invoice was paid', null=True, blank=True)
    amount = models.DecimalField(help_text='Total of the invoice', null=True, blank=True)


def finance_report_file_rename(instance, filename):
    upload_to = 'finance_report/finance_report'

    filename = f'FinanceReport-{instance.id}-ProjectId-{instance.project.id}-{filename}'

    return os.path.join(upload_to, filename)


class FinanceReport(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project of this finance report',
                                on_delete=models.PROTECT)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=finance_report_file_rename)
    due_date = models.DateField(help_text='Date that the finance report was signed', null=True, blank=True)
    sent_date = models.DateField(help_text='Date that the finance report was sent')
    reception_date = models.DateField(help_text='Date that the finance report was received')
    sent_for_approval_date = models.DateField(help_text='Date that the finance report was sent for approval')
    signed_by = models.ForeignKey(PhysicalPerson, help_text='Person who signed the finance report',
                                  on_delete=models.PROTECT)
