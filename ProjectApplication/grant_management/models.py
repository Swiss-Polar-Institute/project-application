from django.contrib.auth.models import User
from django.db import models, transaction
# Create your models here.
# add dates of review, signed date, who signed, grant agreement - need flexibilty in types of dates that are added
from django.db.models import Sum
from django.utils.datetime_safe import datetime
from simple_history.models import HistoricalRecords
from storages.backends.s3boto3 import S3Boto3Storage

from project_core.models import CreateModifyOn, PhysicalPerson, Project
from project_core.utils.utils import management_file_validator, calculate_md5_from_file_field


def grant_agreement_file_rename(instance, filename):
    return f'grant_management/GrantAgreement/Project-{instance.project.key}-{filename}'


class GrantAgreement(CreateModifyOn):
    project = models.OneToOneField(Project, help_text='Project this Grant Agreement belongs to',
                                   on_delete=models.PROTECT)
    signed_date = models.DateField(help_text='Date the grant agreement was signed', null=True, blank=True)
    signed_by = models.ManyToManyField(PhysicalPerson, help_text='People who signed the grant agreement', blank=True)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=grant_agreement_file_rename,
                            validators=[*management_file_validator()])

    def __str__(self):
        return f'{self.project}'

    def signed_by_string(self):
        return ', '.join(
            [f'{person.first_name} {person.surname}' for person in self.signed_by.all().order_by('first_name')])

    @staticmethod
    def comment_object():
        from comments.models import GrantAgreementComment
        return GrantAgreementComment

    @staticmethod
    def attachment_object():
        from comments.models import GrantAgreementAttachment
        return GrantAgreementAttachment

    def attachments(self):
        return self.grantagreementattachment_set.all().order_by('created_on')

    def comments(self):
        return self.grantagreementcomment_set.all().order_by('created_on')


class AbstractProjectDueReceivedDate(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Abstract containing dates',
                                on_delete=models.PROTECT)
    due_date = models.DateField(help_text='Date the document is due', null=True, blank=True)
    received_date = models.DateField(help_text='Date the document was received', null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.project}'


class Installment(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project that this installment refers to', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=11, decimal_places=2, help_text='Installment amount')

    def __str__(self):
        return f'{self.project}-{self.amount}'

    def sent_for_payment(self):
        return self.invoice_set.filter(sent_for_payment_date__isnull=False).aggregate(Sum('amount'))['amount__sum']

    def paid(self):
        return self.invoice_set.filter(paid_date__isnull=False).aggregate(Sum('amount'))['amount__sum']

    def number(self):
        # This is not very efficient, but given the number of invoices and installments it's nice to not have to
        # save this in the database

        installments = list(Installment.objects.filter(project=self.project).order_by('id'))

        return installments.index(self) + 1


def invoice_file_rename(instance, filename):
    return f'grant_management/Invoice/Project-{instance.project.key}-{filename}'


class Invoice(AbstractProjectDueReceivedDate):
    sent_for_payment_date = models.DateField(help_text='Date the invoice was sent for payment', null=True, blank=True)

    file = models.FileField(storage=S3Boto3Storage(), upload_to=invoice_file_rename, null=True,
                            validators=[*management_file_validator()],
                            blank=True)
    paid_date = models.DateField(help_text='Date the invoice was paid', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, help_text='Total of the invoice (CHF)', null=True,
                                 blank=True)
    installment = models.ForeignKey(Installment, help_text='Installment to which the invoice is assigned', null=True,
                                    blank=True, on_delete=models.PROTECT)

    allow_overbudget = models.BooleanField(default=False, help_text='This invoice takes a payment overbudget')
    overbudget_allowed_by = models.ForeignKey(User, null=True, blank=True, help_text='User that allowed the overbudget',
                                              on_delete=models.PROTECT)

    def __str__(self):
        return f'Id: {self.id} Amount: {self.amount}'

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

        return self.installment.number()

    def due_date_passed(self):
        return self.due_date and self.due_date < datetime.today().date() and self.paid_date is None

    def negative(self):
        return self.amount and self.amount < 0

    def comments(self):
        return self.invoicecomment_set.all().order_by('created_on')

    def attachments(self):
        return None


class AbstractProjectReport(AbstractProjectDueReceivedDate):
    sent_for_approval_date = models.DateField(help_text='Date the report was sent for approval', null=True, blank=True)
    approval_date = models.DateField(help_text='Date the report was approved',
                                     blank=True, null=True)
    approved_by = models.ForeignKey(PhysicalPerson, help_text='Person who approved the report',
                                    on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        abstract = True

    def due_date_passed(self):
        return self.due_date and self.due_date < datetime.today().date() and self.approval_date is None


def finance_report_file_rename(instance, filename):
    return f'grant_management/FinancialReport/Project-{instance.project.key}-{filename}'


class FinancialReport(AbstractProjectReport):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=finance_report_file_rename,
                            validators=[*management_file_validator()],
                            blank=True, null=True)


def scientific_report_file_rename(instance, filename):
    return f'grant_management/ScientificReport/Project-{instance.project.key}-{filename}'


class ScientificReport(AbstractProjectReport):
    file = models.FileField(storage=S3Boto3Storage(), upload_to=scientific_report_file_rename,
                            validators=[*management_file_validator()],
                            blank=True, null=True)


class LaySummaryType(CreateModifyOn):
    name = models.CharField(max_length=10,
                            help_text='Type of lay summary which could be used within the application to decide how the'
                                      ' summary is used',
                            unique=True)
    description = models.CharField(max_length=100, help_text='Description of the type of lay summary')

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

    class Meta:
        verbose_name_plural = 'Lay Summaries'


class BlogPost(AbstractProjectDueReceivedDate):
    title = models.CharField(max_length=1024, help_text='Title of the blog post', null=True, blank=True)
    text = models.TextField(help_text='Blog post text', null=True, blank=True)
    author = models.ForeignKey(PhysicalPerson, help_text='Person who wrote the blog post',
                               blank=True, null=True, on_delete=models.PROTECT)

    def media_list(self):
        if self.id:
            return self.medium_set.all().order_by('received_date')
        else:
            return []


class License(CreateModifyOn):
    name = models.CharField(max_length=100,
                            help_text='License name (e.g. Creative Commons Attribution Non Commercial Share Alike 4.0 International)',
                            unique=True)
    spdx_identifier = models.CharField(max_length=100,
                                       help_text='Identifier as per https://spdx.org/licenses/ CC-BY-NC-SA-4.0',
                                       unique=True)
    public_text = models.TextField(
        help_text='Explanatory text for this license. Include the logo and URL to license text.',
        null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


def medium_file_rename(instance, filename):
    return f'grant_management/Medium/Project-{instance.project.key}-{filename}'


class Medium(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project that this medium belongs to', on_delete=models.PROTECT)
    received_date = models.DateField(help_text='Date that the medium was received')
    photographer = models.ForeignKey(PhysicalPerson, help_text='Person who took the photo/video',
                                     on_delete=models.PROTECT)
    license = models.ForeignKey(License, help_text='License',
                                on_delete=models.PROTECT, null=True, blank=True)
    copyright = models.CharField(max_length=1024,
                                 help_text='Owner of copyright if it is not the photographer (e.g. institution)',
                                 null=True, blank=True)
    file = models.FileField(storage=S3Boto3Storage(), upload_to=medium_file_rename,
                            validators=[*management_file_validator()])
    file_md5 = models.CharField(max_length=32, null=True, blank=True)

    blog_posts = models.ManyToManyField(BlogPost, help_text='Which blog posts this image belongs to', blank=True)
    descriptive_text = models.TextField(
        help_text='Description of this media, if provided. Where was it taken, context, etc.', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Media'

    def __str__(self):
        return f'{self.project}-{self.photographer}'

    def save(self, *args, **kwargs):
        self.file_md5 = calculate_md5_from_file_field(self.file)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            MediumDeleted.objects.create(**{'original_id': self.id})
            delete_result = super().delete(*args, **kwargs)

        return delete_result


class MediumDeleted(CreateModifyOn):
    original_id = models.IntegerField(help_text='ID of the delete Medium.ID. Used to return them to the '
                                                'SPI Media Gallery or other software',
                                      unique=True  # The same ID cannot be deleted twice
                                      )

    class Meta:
        verbose_name_plural = 'MediaDeleted'


class SocialNetwork(CreateModifyOn):
    name = models.CharField(max_length=100,
                            help_text='Social network name (e.g. Twitter, Facebook, Instagram, Blog)')

    def __str__(self):
        return f'{self.name}'

    def icon(self):
        return f'external/icons/{self.name.lower()}.png'


class ProjectSocialNetwork(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project to which this social network page is related',
                                on_delete=models.PROTECT)
    social_network = models.ForeignKey(SocialNetwork, help_text='Social network with information about the project',
                                       on_delete=models.PROTECT)
    url = models.URLField(help_text='URL of social network (e.g. https://twitter.com/SwissPolar)', null=True,
                          blank=True)

    def __str__(self):
        return f'{self.project}-{self.social_network}'


def generate_doi_link(doi):
    return f'https://doi.org/{doi}'


class Publication(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project to which the publication is related',
                                on_delete=models.PROTECT)
    doi = models.CharField(max_length=100, help_text='Digital object identifier of publication', null=True, blank=True)
    reference = models.CharField(max_length=1000, help_text='Full reference of publication', null=True, blank=True)
    title = models.CharField(max_length=1000, help_text='Title of publication')
    published_date = models.DateField(help_text='Date on which the resource was published', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.title)

    def doi_link(self):
        return generate_doi_link(self.doi)


class Dataset(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project to which is the dataset is related',
                                on_delete=models.PROTECT)
    doi = models.CharField(max_length=100, help_text='Digital object identifier of dataset', null=True, blank=True)
    url = models.URLField(help_text='URL of dataset if it does not have a DOI', null=True, blank=True)
    title = models.CharField(max_length=1000, help_text='Title of dataset')
    published_date = models.DateField(help_text='Date on which dataset was published', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.title)

    def doi_link(self):
        return generate_doi_link(self.doi)


class MilestoneCategory(CreateModifyOn):
    name = models.CharField(max_length=40)
    created_by = models.ForeignKey(User, help_text='User that created the category', on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Milestone(CreateModifyOn):
    project = models.ForeignKey(Project, help_text='Project to which the milestone is related',
                                on_delete=models.PROTECT)
    due_date = models.DateField()
    category = models.ForeignKey(MilestoneCategory, help_text='Which category is this',
                                 on_delete=models.PROTECT)
    text = models.CharField(max_length=200, blank=True, null=True)

    history = HistoricalRecords()
