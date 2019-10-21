import uuid as uuid_lib

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.validators import validate_email
from django.db import models, transaction
from django.db.models import Max
from django.urls import reverse
from django.utils import timezone


class BudgetCategory(models.Model):
    """Details of budget categories"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of the budget category', max_length=100, blank=False, null=False,
                            unique=True)
    description = models.CharField(help_text='Description of the budget category', max_length=300, blank=False,
                                   null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Budget categories'


class FundingInstrument(models.Model):
    """Details of a funding instrument. This is the highest level of something to which a call can be attributed.
    For example, an exploratory Grant is the funding instrument, and the annual round of applications would come as part
    of a call."""
    long_name = models.CharField(help_text='Full name of funding instrument', max_length=200, blank=False, null=False)
    short_name = models.CharField(help_text='Short name or acronym of the funding instrument', max_length=60, blank=False, null=False)
    description = models.TextField(help_text='Desription of the funding instrument that can be used to distinguish it from others', blank=False, null=False)
    created_by = models.ForeignKey(User, help_text='User id of person creating the funding instrument', related_name='created_by_set', on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time on which the funding instrument was created', default=timezone.now, blank=False, null=False)
    modified_by = models.ForeignKey(User, help_text='User id of person modifying the funding instrument', related_name='modified_by_set', on_delete=models.PROTECT, blank=True, null=True)
    date_modified = models.DateTimeField(help_text='Date and time on which the funding instrument was modified', default=timezone.now, blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.long_name, self.short_name)


class Call(models.Model):
    """Description of call."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    long_name = models.CharField(help_text='Full name of the call', max_length=200, blank=False, null=False,
                                 unique=True)
    short_name = models.CharField(help_text='Short name or acronym of the call', max_length=60, blank=True, null=True)
    description = models.TextField(help_text='Description of the call that can be used to distinguish it from others',
                                   blank=False, null=False)
    funding_instrument = models.ForeignKey(FundingInstrument, help_text='Funding instrument to which the call belongs', blank=True, null=True, on_delete=models.PROTECT)
    introductory_message = models.TextField(help_text='Introductory text to the call for applicants', blank=True,
                                            null=True)
    call_open_date = models.DateTimeField(help_text='Date on which the call is opened', blank=False, null=False)
    submission_deadline = models.DateTimeField(help_text='Submission deadline of the call', blank=False, null=False)
    budget_categories = models.ManyToManyField(BudgetCategory,
                                               help_text='Categories required for the budget for a call')
    budget_maximum = models.DecimalField(help_text='Maximum amount that can be requested in the proposal budget',
                                         decimal_places=2, max_digits=10, validators=[MinValueValidator(0)],
                                         blank=False, null=False)
    created_by = models.ForeignKey(User, help_text='User id of person creating the call',
                                   related_name='call_created_by_set', on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time on which the call was created',
                                        default=timezone.now, blank=False, null=False)
    modified_by = models.ForeignKey(User, help_text='User id of person modifying the call',
                                    related_name='call_modified_by_set', on_delete=models.PROTECT, blank=True, null=True)
    date_modified = models.DateTimeField(help_text='Date and time on which the call was modified',
                                         default=timezone.now, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.long_name

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


class StepType(models.Model):
    """Notable steps during the process"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of a step', max_length=60, blank=False, null=False, unique=True)
    description = models.CharField(help_text='Description of a step', max_length=200, blank=False, null=False)

    def __str__(self):
        return '{}'.format(self.name)


class Step(models.Model):
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


class AbstractQuestion(models.Model):
    """Questions and details relating to their answers that can be used throughout the process"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    TEXT = 'Text'

    TYPES = (
        (TEXT, 'Text'),
    )

    question_text = models.TextField(help_text='Question text', null=False, blank=False)
    question_description = models.TextField(
        help_text='Explanation of question to enable full completion of answer',
        null=True, blank=True)
    answer_type = models.CharField(help_text='Type of field that should be applied to the question answer',
                                   max_length=5, choices=TYPES, default=TEXT, blank=False, null=False)
    answer_max_length = models.PositiveIntegerField(
        help_text='Maximum number of words for a question answer', blank=True, null=True,
        verbose_name='Answer maximum length (in words)')

    def __str__(self):
        return '{}: {} - {}'.format(self.question_text, self.answer_type, self.answer_max_length)

    class Meta:
        abstract = True


class TemplateQuestion(AbstractQuestion):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    def get_absolute_url(self):
        return reverse('question-detail', args=[str(self.pk)])


class CallQuestion(AbstractQuestion):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    call = models.ForeignKey(Call, help_text='Questions for a call', on_delete=models.PROTECT)
    question = models.ForeignKey(TemplateQuestion, help_text='Template question on which this call question is based',
                                 on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time at which the question was added to the call',
                                        default=timezone.now)
    order = models.PositiveIntegerField(help_text='Use the integer order to order the questions', blank=False,
                                        null=False)

    @staticmethod
    def from_template(template_question):
        call_question = CallQuestion()

        call_question.question_text = template_question.question_text
        call_question.question_description = template_question.question_description
        call_question.answer_type = template_question.answer_type
        call_question.answer_max_length = template_question.answer_max_length
        call_question.question = template_question

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
        unique_together = (('call', 'question'), ('call', 'order'),)


class Keyword(models.Model):
    """Set of keywords used to describe the topic of a project, proposal, mission etc. """
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of a keyword', max_length=128, blank=False, null=False)
    description = models.CharField(
        help_text='Description of a keyword that should be used to distinguish it from another keyword', max_length=512,
        blank=False, null=False)
    date_created = models.DateTimeField(help_text='Date and time at which the keyword was created',
                                        default=timezone.now, blank=False, null=False)
    source = models.CharField(help_text='Source from which the keyword originated', max_length=200, blank=False,
                              null=False)

    def __str__(self):
        return '{} - {}'.format(self.name, self.description)

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


class Source(models.Model):
    """Source from where a UID may originate."""

    source = models.CharField(help_text='Source from which a UID or item may originate', max_length=200, blank=False,
                              null=False)
    date_created = models.DateTimeField(help_text='Date and time at which this source was created',
                                        default=timezone.now, blank=False, null=False)

    def __str__(self):
        return '{}'.format(self.source)


class Country(models.Model):
    """Countries"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Country name', max_length=100, blank=False, null=False, unique=True)
    source = models.ForeignKey(Source, help_text='Source of country name', on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time created', default=timezone.now, blank=False,
                                        null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'


class Organisation(models.Model):
    """Details of an organisation - could be scientific, institution, funding etc."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    long_name = models.CharField(help_text='Full name by which the organisation is known', max_length=100, blank=False,
                                 null=False)
    short_name = models.CharField(help_text='Short name by which the organisation is commonly known', max_length=50,
                                  blank=True, null=True)
    street = models.CharField(help_text='Street address of the organisation', max_length=500, blank=False, null=False)
    city = models.CharField(help_text='City in which the organisation is based', max_length=100, blank=False,
                            null=False)
    postal_code = models.CharField(help_text='Postal code of the organisation', max_length=50, blank=False, null=False)
    country = models.ForeignKey(Country, help_text='Country in which the organisation is based', on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time at which the organisation was created',
                                        default=timezone.now, blank=False, null=False)
    source = models.ForeignKey(Source, help_text='Source from which the organisation has originated', on_delete=models.PROTECT)

    def abbreviated_name(self):
        if self.short_name is not None:
            return self.short_name
        else:
            return (self.long_name[:47] + '...') if len(self.long_name) > 50 else self.long_name

    def __str__(self):
        return '{} ({}) - {}'.format(self.long_name, self.short_name, self.country)

    class Meta:
        unique_together = (('long_name', 'country'),)


class Uid(models.Model):
    uid = models.CharField(help_text='Unique identifier', max_length=150, blank=False, null=True)
    source = models.ForeignKey(Source, help_text='Source of the UID', on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time at which this UID was created', default=timezone.now,
                                        blank=False, null=False)

    def __str__(self):
        return '{}: {} {}'.format(self.source, self.uid, self.date_created)

    class Meta:
        abstract = True
        unique_together = (('uid', 'source'),)


class Gender(models.Model):
    """Gender with which a person identifies."""
    name = models.CharField(help_text='Name of gender', max_length=20, blank=False, null=False, unique=True)
    date_created = models.DateTimeField(help_text='Date and time at which this gender was created',
                                        default=timezone.now, blank=False, null=False)

    def __str__(self):
        return '{} {}'.format(self.name, self.date_created)


class PhysicalPerson(models.Model):
    """Information about a unique person."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    first_name = models.CharField(help_text='First name(s) of a person', max_length=100, blank=False, null=False)
    surname = models.CharField(help_text='Last name(s) of a person', max_length=100, blank=False, null=False)
    gender = models.ForeignKey(Gender, help_text='Gender with which the person identifies', blank=True, null=True,
                               on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time at which this person was created',
                                        default=timezone.now, blank=False, null=False)

    def __str__(self):
        return '{} {}: {}'.format(self.first_name, self.surname, self.date_created)

    class Meta:
        unique_together = (('first_name', 'surname',),)


class PersonUid(Uid):
    """UID used for a person"""

    person = models.OneToOneField(PhysicalPerson, help_text='Person to which the UID refers', on_delete=models.PROTECT)

    def __str__(self):
        return '{} {}: {}'.format(self.person, self.source, self.uid)


class PersonPosition(models.Model):
    """Information about a person that may change as they move through their career."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    person = models.ForeignKey(PhysicalPerson, help_text='A unique physical person', on_delete=models.PROTECT)
    academic_title = models.ForeignKey(PersonTitle, help_text='Title of the person', blank=False, null=False,
                                       on_delete=models.PROTECT)
    organisations = models.ManyToManyField(Organisation, help_text='Organisation(s) represented by the person')
    group = models.CharField(help_text='Name of the working group, department, laboratory for which the person works',
                             max_length=200, blank=True, null=True)
    date_created = models.DateTimeField(help_text='Date and time at which this person was created',
                                        default=timezone.now, blank=False, null=False)

    def __str__(self):
        organisations_str = ', '.join([organisation.abbreviated_name() for organisation in self.organisations.all()])

        return '{} {} - {}'.format(self.academic_title, self.person, organisations_str)

    class Meta:
        verbose_name_plural = 'People from organisation(s)'


class Contact(models.Model):
    """Contact details of a person"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    OFFICE = 'Office'
    MOBILE = 'Mobile'
    EMAIL = 'Email'

    METHOD = (
        (OFFICE, 'Office'),
        (MOBILE, 'Mobile'),
        (EMAIL, 'Email'),
    )

    person_position = models.ForeignKey(PersonPosition, help_text='Person to whom the contact details belong',
                                        on_delete=models.PROTECT)
    entry = models.CharField(help_text='Text of contact entry, such as phone number, pager etc.', max_length=100,
                             blank=False, null=False)
    method = models.CharField(help_text='Type of contact method', max_length=30, choices=METHOD, blank=False,
                              null=False)
    date_created = models.DateTimeField(help_text='Date and time at which this contact was created',
                                        default=timezone.now, blank=False, null=False)

    def clean(self):
        if self.method == Contact.EMAIL:
            validate_email(self.entry)

        super().clean()

    def __str__(self):
        return '{} - {}: {}'.format(self.person_position, self.method, self.entry)

    class Meta:
        unique_together = (('person_position', 'entry'),)


class GeographicalArea(models.Model):
    """Geographical area (exact coverage of this not yet determined)"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(help_text='Name of geographic area', max_length=100, blank=False, null=False,
                            unique=True)  # Need to define in more detail if this should be a region, continent, country etc.
    definition = models.CharField(
        help_text='Detailed description of the geographic area to avoid duplicate entries or confusion', max_length=300,
        blank=False, null=False)

    def __str__(self):
        return '{} - {}'.format(self.name, self.definition)


class Proposal(models.Model):
    """Proposal submitted for a call - not yet evaluated and therefore not yet a project."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False, unique=True)

    title = models.CharField(help_text='Title of the proposal being submitted', max_length=500, blank=False, null=False)
    keywords = models.ManyToManyField(Keyword, help_text='Keywords that describe the proposal',
                                      blank=False)
    geographical_areas = models.ManyToManyField(GeographicalArea,
                                                help_text='Geographical area(s) covered by the proposal')
    location = models.CharField(help_text='More precise location of where proposal would take place (not coordinates)',
                                max_length=200, blank=True, null=True)  # Consider having this as another text question
    provisional_start_date = models.DateField(
        help_text='Approximate date on which the proposed project is expected to start',
        blank=False, null=False)
    provisional_end_date = models.DateField(
        help_text='Approximate date on which the proposed project is expected to end',
        blank=False, null=False)
    duration_months = models.DecimalField(
        help_text='Period of time expected that the proposed project will last in months',
        decimal_places=1, max_digits=5, blank=False, null=False)
    applicant = models.ForeignKey(PersonPosition, help_text='Main applicant of the proposal', blank=False, null=False,
                                  on_delete=models.PROTECT)
    proposal_status = models.ForeignKey(ProposalStatus, help_text='Status or outcome of the proposal', blank=False,
                                        null=False, on_delete=models.PROTECT)
    eligibility = models.BooleanField(help_text='Eligibility status of proposal', blank=False, null=False)
    eligibility_comment = models.TextField(help_text='Comments regarding eligibility of proposal', blank=True, null=True)
    call = models.ForeignKey(Call, help_text='Call to which the proposal relates', on_delete=models.PROTECT)
    date_created = models.DateTimeField(help_text='Date and time (UTC) at which the proposal was first created',
                                        default=timezone.now, blank=False, null=False)
    last_modified = models.DateTimeField(help_text='Latest date and time at which the proposal was modified',
                                         default=timezone.now, blank=False, null=False)

    def __str__(self):
        return '{} - {}'.format(self.title, self.applicant)

    def total_budget(self):
        """
        Get the total budget requested by a proposal by summing the items of a budget for a proposal.
        :return: returns total amount of budget
        """

        budget_items = self.budgetitem_set.all()

        total = 0
        for item in budget_items:
            total += item.amount

        return total

    def get_absolute_url(self):
        return reverse('proposal-update', kwargs={'uuid': self.uuid})

    class Meta:
        unique_together = (('title', 'applicant', 'call'),)


class ProposalQAText(models.Model):
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

    organisation = models.ForeignKey(Organisation, help_text='Name of organisation from which the funding is sourced',
                                     blank=False, null=False, on_delete=models.PROTECT)
    funding_status = models.ForeignKey(FundingStatus, help_text='Status of the funding item', blank=False, null=False,
                                       on_delete=models.PROTECT)
    amount = models.DecimalField(help_text='Amount given in funding', decimal_places=2, max_digits=10,
                                 validators=[MinValueValidator(0)], blank=False, null=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} - {}: {}'.format(self.organisation, self.funding_status, self.amount)


class ProposalFundingItem(FundingItem):
    """Specific item of funding for a proposal (referring to funding that has been sourced from elsewhere, rather than
    funding that would result from that proposal being accepted)"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.ForeignKey(Proposal, help_text='Proposal for which the funding has been sourced',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('organisation', 'funding_status', 'proposal', 'amount'),)


class CareerStage(models.Model):
    """Stage of a person within their career."""
    name = models.CharField(help_text='Name of career stage', max_length=50, null=False, blank=False, unique=True)
    description = models.CharField(help_text='Description of the career stage', max_length=100, null=False, blank=False)

    def __str__(self):
        return '{}: {}'.format(self.name, self.description)


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


class Partner(models.Model):
    """Person who is a partner"""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    person = models.ForeignKey(PersonPosition, help_text='Person that is a partner', on_delete=models.PROTECT)
    career_stage = models.ForeignKey(CareerStage, help_text='Stage of the person in the career',
                                     on_delete=models.PROTECT)
    role = models.ForeignKey(Role, help_text='Role of the person', on_delete=models.PROTECT)
    role_description = models.TextField(help_text='Description of what the person will be doing', null=False,
                                        blank=False)
    competences = models.TextField(help_text='Description of the competences of the person', null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} ({}) - {}'.format(self.person, self.career_stage, self.role)


class ProposalPartner(Partner):
    """Partner that is part of a proposal."""
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.ForeignKey(Proposal, help_text='Proposal to on which the partner is collaborating',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('person', 'role', 'proposal'),)


class Comment(models.Model):
    """Comments can be made by a user about an aspect of something contained in the database"""
    text = models.TextField(help_text='Text of a comment', null=False, blank=False)
    time = models.DateTimeField(help_text='Date and time on which a comment was made', null=False, blank=False,
                                default=timezone.now)
    user = models.ForeignKey(User, help_text='User by which the comment was made', on_delete=models.PROTECT)

    class Meta:
        abstract = True
        unique_together = (('time', 'user'),)

    def __str__(self):
        return '{} by {} at {}'.format(self.text, self.time, self.user)


class ProposalComment(Comment):
    """Comments made about a proposal"""
    proposal = models.ForeignKey(Proposal, help_text='Proposal about which the comment was made',
                                 on_delete=models.PROTECT)

    class Meta:
        unique_together = (('proposal', 'time', 'user'),)


class CallComment(Comment):
    """Comments made about a call"""
    call = models.ForeignKey(Call, help_text='Call about which the comment was made', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('call', 'time', 'user'),)
