import calendar
import hashlib
import io
import logging
import uuid as uuid_lib

from botocore.exceptions import EndpointConnectionError, ClientError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.core.validators import validate_email
from django.db import models, transaction
from django.db.models import Max, Sum
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber
from simple_history.models import HistoricalRecords
from storages.backends.s3boto3 import S3Boto3Storage

from . import utils
from .utils.orcid import raise_error_if_orcid_invalid
from .utils.utils import bytes_to_human_readable, external_file_validator

logger = logging.getLogger('project_core')


class CreateModifyOn(models.Model):
    """Details of data creation and modification: including date, time and user."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    created_on = models.DateTimeField(help_text='Date and time at which the entry was created', auto_now_add=True,
                                      blank=False, null=False)
    modified_on = models.DateTimeField(help_text='Date and time at which the entry was modified', auto_now=True,
                                       blank=True, null=True)

    class Meta:
        abstract = True


class FinancialKey(CreateModifyOn):
    name = models.CharField(max_length=20, help_text='Code used by finance (e.g. ECON, TRAVEL) or funding instrument',
                            unique=True)
    description = models.CharField(max_length=200, help_text='Explanation of the code')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    funding_instrument = models.BooleanField(default=True,
                                             help_text='This field is booked or used for a funding instrument')

    def __str__(self):
        return self.name


class BudgetCategory(models.Model):
    """Details of budget categories"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of the budget category', max_length=100, blank=False, null=False,
                            unique=True)
    description = models.CharField(help_text='Description of the budget category', max_length=300, blank=False,
                                   null=False)

    order = models.PositiveIntegerField(help_text='Use the integer order to order the categories', blank=False,
                                        null=False, default=10)

    def __str__(self):
        return self.name

    @staticmethod
    def all_ordered():
        return BudgetCategory.objects.all().order_by('order', 'name')

    class Meta:
        verbose_name_plural = 'Budget categories'


class FundingInstrument(CreateModifyOn):
    """Details of a funding instrument. This is the highest level of something to which a call can be attributed.
    For example, an exploratory Grant is the funding instrument, and the annual round of applications would come as part
    of a call."""
    long_name = models.CharField(help_text='Full name of funding instrument', max_length=200, blank=False, null=False,
                                 unique=True)
    short_name = models.OneToOneField(FinancialKey, help_text='Short name or acronym of the funding instrument',
                                      null=True, on_delete=models.PROTECT)
    description = models.TextField(
        help_text='Description of the funding instrument that can be used to distinguish it from others', blank=False,
        null=False)

    history = HistoricalRecords()

    def __str__(self):
        return '{}'.format(self.long_name)

    def get_absolute_url(self):
        return reverse('logged-funding-instrument-detail', args=[str(self.pk)])


class Call(CreateModifyOn):
    """Description of call."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    long_name = models.CharField(help_text='Full name of the call', max_length=200, blank=False, null=False,
                                 unique=True)
    short_name = models.CharField(help_text='Short name or acronym of the call', max_length=60, blank=True, null=True)
    finance_year = models.IntegerField(
        help_text='Finance year of this call. It is used, for example, for the project key from this call')
    description = models.TextField(help_text='Description of the call that can be used to distinguish it from others',
                                   blank=False, null=False)
    funding_instrument = models.ForeignKey(FundingInstrument, help_text='Funding instrument to which the call belongs',
                                           blank=False, null=False, on_delete=models.PROTECT)
    introductory_message = models.TextField(help_text='Introductory text to the call for applicants', blank=True,
                                            null=True)
    call_open_date = models.DateTimeField(help_text='Date on which the call is opened', blank=False, null=False)
    submission_deadline = models.DateTimeField(help_text='Submission deadline of the call', blank=False, null=False)
    budget_maximum = models.DecimalField(help_text='Maximum amount that can be requested in the proposal budget',
                                         decimal_places=2, max_digits=10, validators=[MinValueValidator(0)],
                                         blank=False, null=False)
    other_funding_question = models.BooleanField(help_text='True if the Other Funding question is enabled')
    proposal_partner_question = models.BooleanField(help_text='True if the Proposal Partner question is enabled')
    overarching_project_question = models.BooleanField(
        help_text='True if the question for the overarching project is displayed',
        default=False)

    history = HistoricalRecords()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.long_name

    def little_name(self):
        if self.short_name:
            return self.short_name
        else:
            return f'{self.long_name[:10]}...'

    @staticmethod
    def open_calls():
        return Call.objects.filter(call_open_date__lte=timezone.now(),
                                   submission_deadline__gte=timezone.now())

    @staticmethod
    def closed_calls():
        return Call.objects.filter(submission_deadline__lte=timezone.now())

    @staticmethod
    def future_calls():
        return Call.objects.filter(call_open_date__gte=timezone.now())

    def number_of_proposals(self):
        return self.proposal_set.count()

    def number_of_proposals_no_draft(self):
        draft = ProposalStatus.objects.get(name=settings.PROPOSAL_STATUS_DRAFT)
        return self.proposal_set.exclude(proposal_status=draft).count()

    def callquestion_set_ordered_by_order(self):
        return self.callquestion_set.all().order_by('order')

    @staticmethod
    def attachment_object():
        from comments.models import CallAttachment
        return CallAttachment

    def attachments(self):
        return self.callattachment_set.all().order_by('created_on')

    def comments(self):
        return self.callcomment_set.all().order_by('created_on')

    @staticmethod
    def comment_object():
        from comments.models import CallComment
        return CallComment

    def evaluation_is_closed(self):
        result = hasattr(self, 'callevaluation') and self.callevaluation.is_closed()
        return result


class BudgetCategoryCall(CreateModifyOn):
    call = models.ForeignKey(Call, blank=False, null=False,
                             help_text='Call where this category is used in',
                             on_delete=models.PROTECT)

    budget_category = models.ForeignKey(BudgetCategory, blank=False, null=False,
                                        help_text='Budget category for this category',
                                        on_delete=models.PROTECT)

    enabled = models.BooleanField(help_text='Appears in the proposal form', default=False)

    order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.budget_category.name

    class Meta:
        unique_together = (('call', 'budget_category'),)


class StepType(models.Model):
    """Notable steps during the process"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of a step', max_length=60, blank=False, null=False, unique=True)
    description = models.CharField(help_text='Description of a step', max_length=200, blank=False, null=False)

    def __str__(self):
        return '{}'.format(self.name)


class Step(CreateModifyOn):
    """Dates of notable steps that are used throughout the process"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    call = models.ForeignKey(Call, help_text='Step within a call', on_delete=models.PROTECT)
    step_type = models.ForeignKey(StepType, help_text='Name of step', max_length=128, null=False,
                                  on_delete=models.PROTECT)
    date = models.DateTimeField(help_text='Date and time of notable date', max_length=64, null=False)

    class Meta:
        unique_together = (('call', 'step_type'),)

    def __str__(self):
        return '{} - {}'.format(self.step_type, self.date)


class AbstractQuestion(CreateModifyOn):
    """Questions and details relating to their answers that can be used throughout the process"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    TEXT = 'Text'
    FILE = 'File'

    TYPES = (
        (TEXT, 'Text'),
        (FILE, 'File')
    )

    question_text = models.TextField(help_text='Question text', null=False, blank=False)
    question_description = models.TextField(
        help_text='Explanation of question to enable full completion of answer',
        null=True, blank=True)
    answer_type = models.CharField(help_text='Type of field that should be applied to the question answer',
                                   max_length=5, choices=TYPES, default=TEXT, blank=False, null=False)
    answer_max_length = models.PositiveIntegerField(
        help_text='Maximum number of words for a question answer', blank=True, null=True,
        verbose_name='Answer maximum length (used for answer type TEXT, in words)')
    answer_required = models.BooleanField(default=True, blank=False, null=False)

    history = HistoricalRecords(inherit=True)

    def __str__(self):
        if self.answer_type == AbstractQuestion.FILE:
            return '{} (FILE, required: {})'.format(self.question_text, self.answer_required)
        elif self.answer_type == AbstractQuestion.TEXT:
            if self.answer_max_length is None:
                return '{} (TEXT, no max words, required: {})'.format(self.question_text, self.answer_required)
            else:
                return '{} (TEXT, max words {}, required: {})'.format(self.question_text, self.answer_max_length,
                                                                      self.answer_required)
        else:
            assert False

    class Meta:
        abstract = True


class TemplateQuestion(AbstractQuestion):
    """Questions used as templates that can be added to calls or other aspects of the forms."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    def get_absolute_url(self):
        return reverse('logged-template-question-detail', args=[str(self.pk)])


class CallQuestion(AbstractQuestion):
    """Questions, taken from the template list, that are part of a call. """
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    call = models.ForeignKey(Call, help_text='Questions for a call', on_delete=models.PROTECT)
    template_question = models.ForeignKey(TemplateQuestion,
                                          help_text='Template question on which this call question is based',
                                          on_delete=models.PROTECT)
    order = models.PositiveIntegerField(
        help_text='Use this number to order the questions',
        blank=False,
        null=False)

    @staticmethod
    def from_template(template_question):
        call_question = CallQuestion()

        call_question.question_text = template_question.question_text
        call_question.question_description = template_question.question_description
        call_question.answer_type = template_question.answer_type
        call_question.answer_max_length = template_question.answer_max_length
        call_question.answer_required = template_question.answer_required
        call_question.template_question = template_question

        return call_question

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.order is None:
            call_questions = CallQuestion.objects.filter(call=self.call)
            if call_questions:
                self.order = call_questions.aggregate(Max('order'))['order__max'] + 1
            else:
                self.order = 1

        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('call', 'template_question'), ('call', 'order'),)


class Source(CreateModifyOn):
    """Source from where a UID or other item originates."""
    source = models.CharField(help_text='Source from which a UID or item may originate', max_length=200, blank=False,
                              null=False)

    description = models.TextField(help_text='Description of the source eg. URL, version', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.source)


class Uid(CreateModifyOn):
    """Uid used to distinguish unique items in vocabulary lists"""
    uid = models.CharField(help_text='Unique identifier', max_length=150, blank=False, null=True)
    source = models.ForeignKey(Source, help_text='Source of the UID', on_delete=models.PROTECT)

    def __str__(self):
        return '{}: {} {}'.format(self.source, self.uid, self.created_on)

    class Meta:
        abstract = True
        unique_together = (('uid', 'source'),)


class KeywordUid(Uid):
    """Uid used to identify a keyword"""
    pass

    def __str__(self):
        return '{}-{}'.format(self.uid, self.source)


class Keyword(CreateModifyOn):
    """Set of keywords used to describe the topic of a project, proposal, mission etc. """
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of a keyword', max_length=128, blank=False, null=False)
    description = models.CharField(
        help_text='Description of a keyword that should be used to distinguish it from another keyword', max_length=512,
        blank=True, null=True)
    uid = models.ForeignKey(KeywordUid, help_text='Source from which the keyword originated', on_delete=models.PROTECT)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        unique_together = (('name', 'description'),)


class ProposalStatus(models.Model):
    """Status options for a proposal"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of the status of the proposal table', max_length=50, blank=False,
                            null=False, unique=True)
    description = models.CharField(help_text='Detailed description of the proposal status name', max_length=512,
                                   blank=False, null=False)

    def __str__(self):
        return '{} - {}'.format(self.name, self.description)

    class Meta:
        verbose_name_plural = 'Proposal status'


class PersonTitle(models.Model):
    """Personal and academic titles"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    title = models.CharField(help_text='Personal or academic title used by a person', max_length=50, blank=False,
                             null=False, unique=True)

    def __str__(self):
        return self.title


class CountryUid(Uid):
    """Uid used to identify a country"""
    pass

    def __str__(self):
        return '{}-{}'.format(self.uid, self.source)


class Country(CreateModifyOn):
    """Countries"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Country name', max_length=100, blank=False, null=False, unique=True)
    uid = models.ForeignKey(CountryUid, help_text='UID of country name', on_delete=models.PROTECT, blank=True,
                            null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'


class OrganisationUid(Uid):
    """Uid used to identify an organisation."""
    pass

    def __str__(self):
        return '{}-{}'.format(self.uid, self.source)


class Organisation(CreateModifyOn):
    """Details of an organisation - could be scientific, institution, funding etc."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    long_name = models.CharField(help_text='Full name by which the organisation is known', max_length=100, blank=False,
                                 null=False)
    short_name = models.CharField(help_text='Short name by which the organisation is commonly known', max_length=50,
                                  blank=True, null=True)
    street = models.CharField(help_text='Street address of the organisation', max_length=500, blank=True, null=True)
    city = models.CharField(help_text='City in which the organisation is based', max_length=100, blank=False,
                            null=False)
    postal_code = models.CharField(help_text='Postal code of the organisation', max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, help_text='Country in which the organisation is based',
                                on_delete=models.PROTECT)
    uid = models.ForeignKey(OrganisationUid, help_text='UID of an organisation', on_delete=models.PROTECT)

    def abbreviated_name(self):
        if self.short_name is not None:
            return self.short_name
        else:
            return (self.long_name[:47] + '...') if len(self.long_name) > 50 else self.long_name

    def __str__(self):
        return '{} - {}'.format(self.long_name, self.country)

    class Meta:
        unique_together = (('long_name', 'country'),)


class OrganisationName(CreateModifyOn):
    """This is used by the dropdown box to the users. Users can add organisation names and will not be associated
    with the organisation until SPI creates the organisation and links it. It's an easy way to allow users to enter
    organisations without details and without having what seems to not exist: a full list of organisations. """
    objects = models.Manager()  # Helps Pycharm CE auto-completion
    name = models.CharField(help_text='A name that the organisation is known for', max_length=100, blank=False,
                            null=False, unique=True)
    organisation = models.ForeignKey(Organisation, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return '{}'.format(self.name)


class Gender(CreateModifyOn):
    """Gender with which a person identifies."""
    name = models.CharField(help_text='Name of gender', max_length=20, blank=False, null=False, unique=True)

    def __str__(self):
        return '{}'.format(self.name)


class PhysicalPerson(CreateModifyOn):
    """Information about a unique person."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    first_name = models.CharField(help_text='First name(s) of a person', max_length=100, blank=False, null=False)
    surname = models.CharField(help_text='Last name(s) of a person', max_length=100, blank=False, null=False)
    orcid = models.CharField(help_text='Orcid ID', max_length=19, blank=False, null=True, unique=True,
                             validators=utils.orcid.orcid_validators())
    gender = models.ForeignKey(Gender, help_text='Gender with which the person identifies', blank=True, null=True,
                               on_delete=models.PROTECT)
    phd_date = models.CharField(help_text='Date (yyyy-mm) on which PhD awarded or expected', max_length=20, blank=True,
                                null=True, validators=[RegexValidator(regex='^[0-9]{4}-[0-9]{2}$',
                                                                      message='Format is yyyy-mm',
                                                                      code='Invalid format')])

    historical = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(self.first_name, self.surname)

    def full_name(self):
        return '{} {}'.format(self.first_name, self.surname)

    def phd_date_formatted(self):
        if self.phd_date is None:
            return None

        year, month = self.phd_date.split('-')
        month = int(month)
        if month < 1 or month > 12:
            return f'{month}-{year}'

        return f'{calendar.month_abbr[int(month)]}. {year}'


class PersonUid(Uid):
    """UID used for a person"""

    person = models.OneToOneField(PhysicalPerson, help_text='Person to which the UID refers', on_delete=models.PROTECT)

    def __str__(self):
        return '{} {}: {}'.format(self.person, self.source, self.uid)


class CareerStage(models.Model):
    """Stage of a person within their career."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of career stage', max_length=50, null=False, blank=False, unique=True)
    description = models.CharField(help_text='Description of the career stage', max_length=100, null=False,
                                   blank=False)
    list_order = models.IntegerField(help_text='Order that this field is displayed', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)


class PersonPosition(CreateModifyOn):
    """Information about a person that may change as they move through their career."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    person = models.ForeignKey(PhysicalPerson, help_text='A unique physical person', on_delete=models.PROTECT)
    academic_title = models.ForeignKey(PersonTitle, help_text='Title of the person', blank=False, null=False,
                                       on_delete=models.PROTECT)
    career_stage = models.ForeignKey(CareerStage, help_text='Stage of the person in the career',
                                     on_delete=models.PROTECT, blank=True, null=True)
    organisation_names = models.ManyToManyField(OrganisationName, help_text='Organisation(s) represented by the person')
    group = models.CharField(help_text='Name of the working group, department, laboratory for which the person works',
                             max_length=200, blank=True, null=True)
    privacy_policy = models.BooleanField(
        help_text='Agree or disagree to the data policy for storage of personal information', default=False,
        blank=False, null=False)
    contact_newsletter = models.BooleanField(help_text='Agree or disagree to being contacted by email with newsletter',
                                             default=False, blank=False, null=False)

    historical = HistoricalRecords()

    def __str__(self):
        organisations_list = []

        for organisation_name in self.organisation_names.all().order_by('name'):
            organisations_list.append(organisation_name.name)

        organisations_str = ', '.join(organisations_list)

        return '{} {} - {}'.format(self.academic_title, self.person, organisations_str)

    def main_email(self):
        email = self.main_email_model()

        if email:
            return email.entry
        else:
            return None

    def main_phone(self):
        phone = self.main_phone_model()

        if phone:
            return phone.entry
        else:
            return None

    def main_phone_uri(self):
        phone = self.main_phone()
        if phone:
            return PhoneNumber.from_string(phone).as_rfc3966
        return None

    def main_email_model(self):
        emails = self.contact_set.filter(method=Contact.EMAIL).order_by('created_on')

        if emails:
            return emails[0]
        else:
            return None

    def main_phone_model(self):
        phones = self.contact_set.filter(method=Contact.PHONE).order_by('created_on')

        if phones:
            return phones[0]
        else:
            return None

    def organisations_ordered_by_name(self):
        return self.organisation_names.all().order_by('name')

    def organisations_ordered_by_name_str(self):
        organisations = []

        for organisation in self.organisations_ordered_by_name():
            if organisation.organisation is None:
                organisations.append(organisation.name)
            else:
                organisations.append(organisation.organisation.long_name)

        return ', '.join(organisations)


class Contact(CreateModifyOn):
    """Contact details of a person"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    OFFICE = 'Office'
    MOBILE = 'Mobile'
    EMAIL = 'Email'
    PHONE = 'Phone'

    METHOD = (
        (OFFICE, 'Office'),
        (MOBILE, 'Mobile'),
        (EMAIL, 'Email'),
        (PHONE, 'Phone')
    )

    person_position = models.ForeignKey(PersonPosition, help_text='Person to whom the contact details belong',
                                        on_delete=models.PROTECT)
    entry = models.CharField(help_text='Text of contact entry, such as phone number, pager etc.', max_length=100,
                             blank=False, null=False)
    method = models.CharField(help_text='Type of contact method', max_length=30, choices=METHOD, blank=False,
                              null=False)

    history = HistoricalRecords()

    def clean(self):
        if self.method == Contact.EMAIL:
            validate_email(self.entry)

        super().clean()

    def __str__(self):
        return '{} - {}: {}'.format(self.person_position, self.method, self.entry)

    class Meta:
        unique_together = (('person_position', 'entry', 'method'),)


class GeographicalAreaUid(Uid):
    """UID of a geographical area."""
    pass

    def __str__(self):
        return '{}-{}'.format(self.uid, self.source)


class GeographicalArea(CreateModifyOn):
    """Geographical area (exact coverage of this not yet determined)"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of geographic area', max_length=100, blank=False, null=False, unique=True)
    definition = models.CharField(
        help_text='Detailed description of the geographic area to avoid duplicate entries or confusion', max_length=300,
        blank=False, null=False)
    uid = models.ForeignKey(GeographicalAreaUid, help_text='UID of a geographical area', on_delete=models.PROTECT,
                            blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)


class ExternalProject(CreateModifyOn):
    title = models.CharField(help_text='Title of the project', max_length=500, blank=False, null=False)
    leader = models.ForeignKey(PersonPosition, help_text='Leader of this project',
                               blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.title} - {self.leader}'


class PostalAddress(CreateModifyOn):
    # We've decided to not normalise this model
    address = models.TextField(help_text='Department name, street/avenue, block, building, floor, door, etc.')

    city = models.CharField(max_length=256)
    postcode = models.CharField(max_length=128)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)


class Role(models.Model):
    """Role a person can take in a variety of different circumstances."""
    PROPOSAL = 'Proposal'
    PROJECT = 'Project'
    EXPEDITION = 'Expedition'

    TYPES = (
        (PROPOSAL, 'Proposal'),
        (PROJECT, 'Project'),
        (EXPEDITION, 'Expedition'),
    )

    name = models.CharField(help_text='Name of role', max_length=50, null=False, blank=False)
    description = models.CharField(help_text='Description of role to distinguish it from others', max_length=200,
                                   null=False, blank=False)
    type = models.CharField(
        help_text='Part of the application to which the role refers, determining where it can be used in some cases',
        choices=TYPES, max_length=25, null=False, blank=False)

    def __str__(self):
        return '{} ({}): {}'.format(self.name, self.type, self.description)

    class Meta:
        unique_together = (('name', 'type'),)


class RoleDescription(CreateModifyOn):
    # It holds the description of a Role for a Partner, Applicant, etc. (a person with a role)
    role = models.ForeignKey(Role, help_text='Role of the partner', on_delete=models.PROTECT)
    description = models.TextField(help_text="Description of the role", null=False,
                                   blank=False)
    competences = models.TextField(help_text="Description of the key competences", null=False, blank=False)


class Proposal(CreateModifyOn):
    """Proposal submitted for a call - not yet evaluated and therefore not yet a project."""
    ELIGIBILITYNOTCHECKED = 'Eligibility not checked'
    ELIGIBLE = 'Eligible'
    NOTELIGIBLE = 'Not eligible'

    STATUS = (
        (ELIGIBILITYNOTCHECKED, 'Eligibility not checked'),
        (ELIGIBLE, 'Eligible'),
        (NOTELIGIBLE, 'Not eligible'),
    )

    objects = models.Manager()  # Helps Pycharm CE auto-completion

    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False, unique=True)

    title = models.CharField(help_text='Title of the proposal being submitted', max_length=500, blank=False, null=False)
    postal_address = models.ForeignKey(PostalAddress,
                                       help_text='Address to where the grant agreement is going to be sent',
                                       null=True,
                                       on_delete=models.PROTECT)
    keywords = models.ManyToManyField(Keyword, help_text='Keywords that describe the proposal',
                                      blank=False)
    geographical_areas = models.ManyToManyField(GeographicalArea,
                                                help_text='Geographical area(s) covered by the proposal')
    location = models.CharField(
        help_text='Name of more precise location of where proposal would take place (not coordinates)',
        max_length=200, blank=True, null=True)  # Consider having this as another text question
    start_date = models.DateField(
        help_text='Approximate date on which the proposed project is expected to start',
        blank=False, null=False)
    end_date = models.DateField(
        help_text='Approximate date on which the proposed project is expected to end',
        blank=False, null=False)
    duration_months = models.DecimalField(
        help_text='Expected duration of the proposed project in months',
        decimal_places=1, max_digits=5, validators=[MinValueValidator(0)], blank=False, null=False)
    applicant = models.ForeignKey(PersonPosition, help_text='Main applicant of the proposal', blank=False, null=False,
                                  on_delete=models.PROTECT)
    applicant_role_description = models.ForeignKey(RoleDescription, help_text='Main applicant role', blank=True,
                                                   null=True,
                                                   on_delete=models.PROTECT)
    proposal_status = models.ForeignKey(ProposalStatus, help_text='Status or outcome of the proposal', blank=False,
                                        null=False, on_delete=models.PROTECT)
    eligibility = models.CharField(help_text='Status of eligibility of proposal', max_length=30,
                                   default=ELIGIBILITYNOTCHECKED, choices=STATUS, blank=False, null=False)
    eligibility_comment = models.TextField(help_text='Comments regarding eligibility of proposal', blank=True,
                                           null=True)
    call = models.ForeignKey(Call, help_text='Call to which the proposal relates', on_delete=models.PROTECT)

    overarching_project = models.ForeignKey(ExternalProject, null=True, blank=True, on_delete=models.PROTECT)

    draft_saved_mail_sent = models.BooleanField(default=False,
                                                help_text='True if the email informing the applicant that the draft has been saved has already been sent (usually is sent only once)')

    submitted_mail_sent = models.BooleanField(default=False,
                                              help_text='True if the email informing the applicant that the proposal has been submitted has been sent')

    history = HistoricalRecords()

    def __str__(self):
        return '{} - {}'.format(self.title, self.applicant)

    def keywords_enumeration(self):
        keywords = self.keywords.all().order_by('name')

        if keywords:
            return ', '.join([keyword.name for keyword in keywords])
        else:
            return '-'

    def geographical_areas_enumeration(self):
        geographical_areas = self.geographical_areas.all().order_by('name')
        if geographical_areas:
            return ', '.join([geographical_area.name for geographical_area in geographical_areas])
        else:
            return '-'

    def total_budget(self):
        """
        Get the total budget requested by a proposal by summing the items of a budget for a proposal.
        :return: returns total amount of budget
        """

        budget_items = self.proposedbudgetitem_set.all()

        total = 0
        for item in budget_items:
            if item.amount is not None:
                total += item.amount

        return total

    def get_absolute_url(self):
        return reverse('proposal-update', kwargs={'uuid': self.uuid})

    def status_is_draft(self):
        return self.proposal_status.name == settings.PROPOSAL_STATUS_DRAFT

    def status_is_submitted(self):
        return self.proposal_status.name == settings.PROPOSAL_STATUS_SUBMITTED

    def eligibility_is_eligible(self):
        return self.eligibility == Proposal.ELIGIBLE

    def attachments(self):
        return self.proposalattachment_set.all().order_by('created_on')

    def comments(self):
        return self.proposalcomment_set.all().order_by('created_on')

    @staticmethod
    def attachment_object():
        from comments.models import ProposalAttachment
        return ProposalAttachment

    @staticmethod
    def comment_object():
        from comments.models import ProposalComment
        return ProposalComment

    def can_eligibility_be_created_or_changed(self):
        # TODO: if there is a project for this proposal it cannot be changed anymore
        return not self.status_is_draft()

    def reason_eligibility_cannot_be_created_or_changed(self):
        if self.status_is_draft():
            return 'Proposal status cannot be draft in order to create/edit eligibility'

        # TODO: if can_eligibility_be_created_or_changed returned False because a project exists for this
        # proposal: explain it here

        assert False

    def can_call_evaluation_be_visualised(self):
        return hasattr(self.call, 'callevaluation')

    def can_create_evaluation(self):
        return self.status_is_submitted() and self.eligibility_is_eligible() and \
               hasattr(self.call, 'callevaluation') and self.call.callevaluation.is_open()

    def reason_cannot_create_evaluation(self):
        if not self.status_is_submitted():
            return 'To evaluate the proposal the status needs to be submitted'
        elif not self.eligibility_is_eligible():
            return 'To evaluate the proposal eligibility needs to be eligible'
        elif not hasattr(self.call, 'callevaluation'):
            return 'To evaluate the proposal a Call Evaluation needs to be created'
        elif not self.call.callevaluation.is_open():
            return 'To evaluate the proposal the Call Evaluation needs to be open'

        assert False

    class Meta:
        unique_together = (('title', 'applicant', 'call'),)

    def can_eligibility_be_edited(self):
        return self.can_eligibility_be_created_or_changed() and not hasattr(self, 'proposalevaluation')

    def reason_cannot_eligibility_be_edited(self):
        if not self.can_eligibility_be_created_or_changed():
            return self.reason_eligibility_cannot_be_created_or_changed()
        elif self.proposalevaluation:
            return 'Eligibility cannot be changed because a proposal evaluation already exists'


class ProposalQAText(CreateModifyOn):
    """Questions assigned to a proposal and their respective answers"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.ForeignKey(Proposal, help_text='Questions and answers for a proposal', on_delete=models.PROTECT)
    call_question = models.ForeignKey(CallQuestion, help_text='Question from the call', on_delete=models.PROTECT)
    answer = models.TextField(help_text='Answer to the question from the call', blank=False, null=False)

    def __str__(self):
        return 'Q: {}; A: {}'.format(self.call_question, self.answer)

    class Meta:
        verbose_name_plural = 'Proposal question-answer (text)'
        unique_together = (('proposal', 'call_question'),)


class ProposalQAFile(CreateModifyOn):
    proposal = models.ForeignKey(Proposal, help_text='Proposal that this file is attached to', on_delete=models.PROTECT)
    call_question = models.ForeignKey(CallQuestion, help_text='Question from the call', on_delete=models.PROTECT)
    file = models.FileField(storage=S3Boto3Storage(),
                            upload_to='proposals_qa/',
                            validators=[*external_file_validator()])
    # Using md5 so it matches (usually) ETags
    md5 = models.CharField(db_index=True, max_length=32)

    def human_file_size(self):
        try:
            return bytes_to_human_readable(self.file.size)
        except EndpointConnectionError:
            logger.warning(f'NOTIFY: ProposalQAFile {self.id} EndpointConnectionError')
            return 'Unknown -EndpointConnectionError'
        except ClientError:
            logger.warning(f'NOTIFY: ProposalQAFile {self.id} ClientError')
            return 'Unknown -ClientError'

    def save(self, *args, **kwargs):
        if self.file:
            self.md5 = self._calculate_md5()
        else:
            # Actually if there is no file this should not be called
            self.md5 = None

        super().save(*args, **kwargs)

    def _calculate_md5(self):
        # initial_position = self.file.file.file.pos()
        # self.file.file.file.seek(0)

        if type(self.file.file.file) == io.BytesIO:
            file_contents = self.file.file.file.getvalue()
        else:
            # This is horrible. It happens when the file is updated
            # (at least in our flow)
            file_contents = self.file.file.read()

        hash_md5 = hashlib.md5(file_contents)

        # self.file.file.file.seek(initial_position)

        return hash_md5.hexdigest()

    def __str__(self):
        return 'Q: {}; A: file'.format(self.call_question)


class BudgetItem(models.Model):
    """Itemised line in a budget, comprising of a category, full details and the amount"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    category = models.ForeignKey(BudgetCategory, help_text='Name of the budget item', blank=False, null=False,
                                 on_delete=models.PROTECT)
    details = models.TextField(help_text='Details of the budget item', blank=True, null=False)
    amount = models.DecimalField(help_text='Cost of category item', decimal_places=2, max_digits=10,
                                 validators=[MinValueValidator(0)], blank=False, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}: {}'.format(self.category, self.amount)


class ProposedBudgetItem(BudgetItem):
    """Itemised line in a budget as part of a proposal"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.ForeignKey(Proposal, help_text='Proposal it which the budget item relates',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('category', 'proposal',),)


class FundingStatus(models.Model):
    """Status of funding"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    status = models.CharField(help_text='Name of the status', max_length=30, blank=False, null=False, unique=True)
    description = models.CharField(help_text='Description of the status', max_length=100, blank=False, null=False)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name_plural = 'Funding status'


class FundingItem(models.Model):
    """Specific item of funding"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    organisation_name = models.ForeignKey(OrganisationName,
                                          help_text='Name of organisation from which the funding is sourced',
                                          blank=False, null=False, on_delete=models.PROTECT)
    funding_status = models.ForeignKey(FundingStatus, help_text='Status of the funding', blank=False, null=False,
                                       on_delete=models.PROTECT)
    amount = models.DecimalField(help_text='Amount given in funding', decimal_places=2, max_digits=10,
                                 validators=[MinValueValidator(0)], blank=False, null=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} - {}: {}'.format(self.organisation_name, self.funding_status, self.amount)


class ProposalFundingItem(FundingItem):
    """Specific item of funding for a proposal (referring to funding that has been sourced from elsewhere, rather than
    funding that would result from that proposal being accepted)"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.ForeignKey(Proposal, help_text='Proposal for which the funding has been sourced',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('organisation_name', 'funding_status', 'proposal', 'amount'),)


class Partner(models.Model):
    """Person who is a partner"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    person = models.ForeignKey(PersonPosition, help_text='Person that is a partner', on_delete=models.PROTECT)
    role = models.ForeignKey(Role, help_text='Role of the partner', on_delete=models.PROTECT)
    role_description = models.TextField(help_text="Description of the partner's role", null=False,
                                        blank=False)
    competences = models.TextField(help_text="Description of the partner's key competences", null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} - {}'.format(self.person, self.role)


class ProposalPartner(Partner):
    """Partner that is part of a proposal."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.ForeignKey(Proposal, help_text='Proposal to on which the partner is collaborating',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('person', 'role', 'proposal'),)


class Project(CreateModifyOn):
    """Proposal that has been funded is now a project. Otherwise another project that has been accepted."""

    objects = models.Manager()  # Helps Pycharm CE auto-completion

    ONGOING = 'Ongoing'
    COMPLETED = 'Completed'
    ABORTED = 'Aborted'

    STATUS = (
        (ONGOING, 'Ongoing'),
        (COMPLETED, 'Completed'),
        (ABORTED, 'Aborted'),
    )

    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False, unique=True)
    key = models.CharField(help_text='Project key identifier all the way to finance', max_length=64, unique=True)
    title = models.CharField(help_text='Title of the project', max_length=500, blank=False, null=False)
    keywords = models.ManyToManyField(Keyword, help_text='Keywords that describe the project',
                                      blank=False)
    geographical_areas = models.ManyToManyField(GeographicalArea,
                                                help_text='Geographical area(s) covered by the project')
    location = models.CharField(
        help_text='Name of more precise location of where the project would take place (not coordinates)',
        max_length=200, blank=True, null=True)
    start_date = models.DateField(
        help_text='Date on which the project is expected to start',
        blank=False, null=False)
    end_date = models.DateField(
        help_text='Date on which the project is expected to end',
        blank=False, null=False)
    principal_investigator = models.ForeignKey(PersonPosition, help_text='Main applicant of the project', blank=False,
                                               null=False,
                                               on_delete=models.PROTECT)  # maybe rename this to principal investigator
    call = models.ForeignKey(Call, help_text='Call to which the project belongs', blank=False, null=False,
                             on_delete=models.PROTECT)
    proposal = models.ForeignKey(Proposal, help_text='Proposal from which the project originates', blank=True,
                                 null=True, on_delete=models.PROTECT)
    overarching_project = models.ForeignKey(ExternalProject,
                                            help_text='Overarching project to which this project contributes',
                                            blank=True, null=True, on_delete=models.PROTECT)
    allocated_budget = models.DecimalField(help_text='Budget allocated to project', decimal_places=2, max_digits=10,
                                           validators=[MinValueValidator(0)], blank=False, null=False)
    status = models.CharField(help_text='Status of a project', max_length=30, default=ONGOING, choices=STATUS,
                              blank=False, null=False)
    abortion_reason = models.CharField(help_text='Reason that a project was aborted', max_length=50, blank=True,
                                       null=True)

    closed_on = models.DateTimeField(help_text='When the project was closed', null=True)
    closed_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    supervisor = models.ForeignKey(PersonPosition, help_text='Supervisor', blank=True, null=True,
                                   on_delete=models.PROTECT, related_name='supervisor')

    history = HistoricalRecords()

    def __str__(self):
        return '{} - {}'.format(self.title, self.principal_investigator)

    def key_pi(self):
        return f'{self.key} {self.principal_investigator.person.surname}'

    def keywords_enumeration(self):
        keywords = self.keywords.all().order_by('name')

        if keywords:
            return ', '.join([keyword.name for keyword in keywords])
        else:
            return '-'

    def geographical_areas_enumeration(self):
        geographical_areas = self.geographical_areas.all().order_by('name')
        if geographical_areas:
            return ', '.join([geographical_area.name for geographical_area in geographical_areas])
        else:
            return '-'

    @staticmethod
    def comment_object():
        from comments.models import ProjectComment
        return ProjectComment

    @staticmethod
    def attachment_object():
        from comments.models import ProjectAttachment
        return ProjectAttachment

    @staticmethod
    def create_from_proposal(proposal, sequence):
        project = Project()

        project.title = proposal.title
        project.key = f'{proposal.call.funding_instrument.short_name}-{proposal.call.finance_year}-{sequence:03d}'
        project.location = proposal.location
        project.start_date = proposal.start_date
        project.end_date = proposal.end_date
        project.principal_investigator = proposal.applicant

        project.overarching_project = proposal.overarching_project
        project.allocated_budget = proposal.proposalevaluation.allocated_budget
        project.status = Project.ONGOING

        project.call = proposal.call
        project.proposal = proposal

        project.save()
        project.geographical_areas.add(*proposal.geographical_areas.all())
        project.keywords.add(*proposal.keywords.all())

        return project

    def attachments(self):
        return self.projectattachment_set.all().order_by('created_on')

    def comments(self):
        return self.projectcomment_set.all().order_by('created_on')

    def main_lay_summary_web(self):
        from grant_management.models import LaySummaryType
        lay_summary_type_web = LaySummaryType.objects.get(name='Web')

        lay_summaries = self.laysummary_set.filter(lay_summary_type=lay_summary_type_web).order_by('-created_on')

        if lay_summaries:
            return lay_summaries[0].text
        else:
            return None

    def invoices_sent_for_payment_amount(self):
        return self.invoice_set.filter(sent_for_payment_date__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0

    def invoices_paid_amount(self):
        return self.invoice_set.filter(paid_date__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0

    def number_of_comments_in_invoices(self):
        total = 0

        for invoice in self.invoice_set.all():
            total += len(invoice.comments())

        return total

    def is_active(self):
        return self.status == Project.ONGOING

    class Meta:
        unique_together = (('title', 'principal_investigator', 'call'),)


class ProjectPartner(Partner):
    """Partner that is part of a project."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    project = models.ForeignKey(Project, help_text='Project on which the partner is collaborating',
                                on_delete=models.PROTECT)

    class Meta:
        unique_together = (('person', 'role', 'project'),)
