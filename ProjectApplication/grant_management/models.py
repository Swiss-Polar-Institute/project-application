from django.db import models
# Create your models here.
# add dates of review, signed date, who signed, grant agreement - need flexibilty in types of dates that are added
from storages.backends.s3boto3 import S3Boto3Storage

from project_core.models import CreateModifyOn, PhysicalPerson, Project


def grant_agreement_file_rename(instance, filename):
    return f'grant_management/GrantAgreement/Project-{instance.project.id:04}-{filename}'


class GrantAgreement(CreateModifyOn):
    project = models.OneToOneField(Project, help_text='Project this Grant Agreement belongs to',
                                   on_delete=models.PROTECT)
    signed_date = models.DateField(help_text='Date the grant agreement was signed', null=True, blank=True)
    signed_by = models.ManyToManyField(PhysicalPerson, help_text='People who signed the grant agreement')
    file = models.FileField(storage=S3Boto3Storage(), upload_to=grant_agreement_file_rename)

    def signed_by_string(self):
        return ', '.join([f'{person.first_name} {person.surname}' for person in self.signed_by.all().order_by('first_name')])

    def __str__(self):
        return f'{self.project}'


class AbstractProjectDueReceivedDate(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Abstract containing dates',
                                on_delete=models.PROTECT)
    due_date = models.DateField(help_text='Date the document is due')
    received_date = models.DateField(help_text='Date the document was received', null=True, blank=True)

    def __str__(self):
        return f'{self.project}'

    class Meta:
        abstract = True


class Installment(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project that this installment refers to', on_delete=models.PROTECT)
    due_date = models.DateField(help_text='Due date of this instalment')
    amount = models.DecimalField(max_digits=11, decimal_places=2, help_text='Amount of this instalment')

    def __str__(self):
        return f'{self.project}-{self.due_date}-{self.amount}'


def invoice_file_rename(instance, filename):
    return f'grant_management/Invoice/Project-{instance.project.id:04}-{filename}'


class Invoice(AbstractProjectDueReceivedDate):
    sent_for_payment_date = models.DateField(help_text='Date the invoice was sent for payment', null=True, blank=True)

    file = models.FileField(storage=S3Boto3Storage(), upload_to=invoice_file_rename, null=True, blank=True)
    paid_date = models.DateField(help_text='Date the invoice was paid', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, help_text='Total of the invoice (CHF)', null=True,
                                 blank=True)
    installment = models.ForeignKey(Installment, help_text='Which installment this invoice refers to', null=True,
                                    blank=True, on_delete=models.PROTECT)

    @staticmethod
    def comment_object():
        from comments.models import InvoiceComment
        return InvoiceComment

    @staticmethod
    def attachment_object():
        return None

    def installment_number(self):
        # This is not very efficient, but given the number of invoices and installments it's nice to not have to
        # save this in the database

        if self.installment is None:
            return None

        installments = list(Installment.objects.filter(project=self.project).order_by('due_date'))

        return installments.index(self.installment) + 1

    def comments(self):
        return self.invoicecomment_set.all().order_by('created_on')

    def attachments(self):
        return None

    def __str__(self):
        return f'Id: {self.id} Amount: {self.amount}'


class AbstractProjectReport(AbstractProjectDueReceivedDate):
    sent_for_approval_date = models.DateField(help_text='Date the report was sent for approval', null=True, blank=True)
    approval_date = models.DateField(help_text='Date the report was approved',
                                     blank=True, null=True)
    approved_by = models.ForeignKey(PhysicalPerson, help_text='Person who approved the report',
                                    on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        abstract = True


def finance_report_file_rename(instance, filename):
    return f'grant_management/FinancialReport/Project-{instance.project.id:04}-{filename}'


class FinancialReport(AbstractProjectReport):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=finance_report_file_rename, blank=True, null=True)


def scientific_report_file_rename(instance, filename):
    return f'grant_management/ScientificReport/Project-{instance.project.id:04}-{filename}'


class ScientificReport(AbstractProjectReport):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=scientific_report_file_rename, blank=True, null=True)


class LaySummaryType(CreateModifyOn):
    name = models.CharField(max_length=10,
                            help_text='Type of lay summary which could be used within the application to decide how the'
                                      ' summary is used',
                            unique=True, blank=False, null=False)
    description = models.CharField(max_length=100, help_text='Description of the type of lay summary', blank=False,
                                   null=False)

    def __str__(self):
        return self.name


class LaySummary(AbstractProjectDueReceivedDate):
    text = models.TextField(help_text='Lay summary text', null=True, blank=True)
    lay_summary_type = models.ForeignKey(LaySummaryType, help_text='Type of the lay summary', blank=True, null=True,
                                         on_delete=models.PROTECT)
    author = models.ForeignKey(PhysicalPerson, help_text='Person who wrote the lay summary',
                               blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.text[:20]}'


class BlogPost(AbstractProjectDueReceivedDate):
    text = models.TextField(help_text='Blog post text', null=True, blank=True)
    author = models.ForeignKey(PhysicalPerson, help_text='Person who wrote the blog post',
                               blank=True, null=True, on_delete=models.PROTECT)


class License(CreateModifyOn):
    name = models.CharField(max_length=30, help_text='License name', null=False, blank=False)
    public_text = models.CharField(max_length=200,
                                   help_text='Explanatory text for this license. Include the logo and URL to license text.',
                                   null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Media(AbstractProjectDueReceivedDate):
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
