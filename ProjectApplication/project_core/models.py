from django.db import models


# Create your models here.
from django.db.models import CharField


class Step(models.Model):
    """Notable steps during the process"""
    name = models.CharField(help_text='Name of a step', max_length=60, blank=False, null=False)
    description = models.CharField(help_text='Description of a step', max_length=200, blank=False, null=False)

    def __str__(self):
        return '{}'.format(self.name)


class StepDate(models.Model):
    """Dates of notable steps that are used throughout the process"""
    step = models.ForeignKey(Step, help_text='Name of step',max_length=128, null=False, on_delete=models.PROTECT)
    date = models.DateTimeField(help_text='Date and time of notable date',max_length=64, null=False)

    def __str__(self):
        return '{} - {}'.format(self.step, self.date)


class Message(models.Model):
    """Messages that can be used throughout the SPI projects application"""
    CALL_INTRODUCTORY_MESSAGE = 'CI'

    MESSAGES= (
        (CALL_INTRODUCTORY_MESSAGE, 'Call introductory message'),
    )

    message_type = models.CharField(help_text='Identification of where the message is to be used', max_length=5, choices=MESSAGES, blank=False, null=False)
    message = models.TextField(help_text='Text of the message', blank=False, null=False)

    def __str__(self):
        return self.message


class BudgetCategory(models.Model):
    """Details of budget categories"""
    name = models.CharField(help_text='Name of the budget category', max_length=100, blank=False, null=False)
    description = models.CharField(help_text='Description of the budget category', max_length=300, blank=False, null=False)
    
    def __str__(self):
        return self.name


class Call(models.Model):
    """Description of call."""
    long_name = models.CharField(help_text='Full name of the call', max_length=200, blank=False, null=False)
    short_name = models.CharField(help_text='Short name or acronym of the call', max_length=60, blank=True, null=True)
    description = models.TextField(help_text='Description of the call that can be used to distinguish it from others', blank=False, null=False)
    introductory_message = models.TextField(help_text='Introductory text to the call for applicants', blank=True, null=True)
    call_open_date = models.DateTimeField(help_text='Date on which the call is opened', blank=False, null=False)
    submission_deadline = models.DateTimeField(help_text='Submission deadline of the call', blank=False, null=False)
    budget_categories = models.ManyToManyField(BudgetCategory, help_text='Categories required for the budget for a call')
    budget_maximum = models.DecimalField(help_text='Maximum amount that can be requested in the proposal budget', decimal_places=2, max_digits=10, blank=False, null=False)

    def __str__(self):
        return self.long_name


class Keyword(models.Model):
    """Set of keywords used to describe the topic of a project, proposal, mission etc. """
    name = models.CharField(help_text='Name of a keyword', max_length=128, blank=False, null=False)
    description = models.CharField(help_text='Decsription of a keyword that should be used to distinguish it from another keyword', max_length=512, blank=False, null=False)

    def __str__(self):
        return '{} - {}'.format(self.name, self.description)


class ProposalStatus(models.Model):
    """Status options for a proposal"""
    name = models.CharField(help_text='Name of the status of the proposal table', max_length=50, blank=False, null=False)
    description = models.CharField(help_text='Detailed description of the proposal status name', max_length=512, blank=False, null=False)

    def __str__(self):
        return '{} - {}'.format(self.name, self.description)


class PersonTitle(models.Model):
    """Personal and academic titles"""
    title = models.CharField(help_text='Personal or academic title used by a person', max_length=50, blank=False, null=False)
    
    def __str__(self):
        return self.title


class Country(models.Model):
    """Countries"""
    name = models.CharField(help_text='Country name', max_length=100, blank=False, null=False)
    
    def __str__(self):
        return self.name


class Organisation(models.Model):
    """Details of an organisation - could be scientific, institution, funding etc."""
    long_name = models.CharField(help_text='Full name by which the organisation is known', max_length=100, blank=False, null=False)
    short_name = models.CharField(help_text='Short name by which the organisation is commonly known', max_length=50, blank=True, null=True)
    address = models.CharField(help_text='Address of the organisation', max_length=1000, blank=True, null=True)
    country = models.ForeignKey(Country, help_text='Country in which the organisation is based', on_delete=models.PROTECT)
    
    def __str__(self):
        return '{} ({}) - {}'.format(self.long_name, self.short_name, self.country)


class Person(models.Model):
    """Information about a person."""
    academic_title = models.ForeignKey(PersonTitle, help_text='Title of the person', blank=False, null=False, on_delete=models.PROTECT)
    first_name = models.CharField(help_text='First name(s) of a person', max_length=100, blank=False, null=False)
    surname = models.CharField(help_text='Last name(s) of a person', max_length=100, blank=False, null=False)
    organisation = models.ManyToManyField(Organisation, help_text='Organisation(s) represented by the person')
    group = models.CharField(help_text='Name of the working group, department, laboratory for which the person works', max_length=200, blank=True, null=True)

    def __str__(self):
        return '{} {} - {}'.format(self.first_name, self.surname, ', '.join(self.organisation.all()))


class Contact(models.Model):
    """Contact details of a person"""
    email_address = models.CharField(help_text='Email address', max_length=100, blank=False, null=False)
    work_telephone = models.CharField(help_text='Work telephone number', max_length=20, blank=False, null=False)
    mobile = models.CharField(help_text='Mobile telephone number', max_length=20, blank=True, null=True)
    person = models.ForeignKey(Person, help_text='Person to which the contact details belong', on_delete=models.PROTECT)

    def __str__(self):
        return '{} - {}'.format(self.person, self.email_address)


class GeographicArea(models.Model):
    """Geographical area (exact coverage of this not yet determined)"""
    area = models.CharField(help_text='Name of geograpic area', max_length=100, blank=False, null=False) # Need to define in more detail if this should be a region, continent, country etc.
    definition = models.CharField(help_text='Detailed description of the geographic area to avoid duplicate entries or confusion', max_length=300, blank=False, null=False)

    def __str__(self):
        return '{} - {}'.format(self.area, self.definition)


class Proposal(models.Model):
    """Proposal submitted for a call - not yet evaluated and therefore not yet a project."""
    title = models.CharField(help_text='Title of the proposal being submitted', max_length=1000, blank=False, null=False)
    keywords = models.ManyToManyField(Keyword, help_text='Keywords that describe the topic of the proposal', blank=False)
    geographical_area = models.ForeignKey(GeographicArea, help_text='Description of the geographical area covered by the proposal', blank=False, null=False,on_delete=models.PROTECT)
    location = models.CharField(help_text='More precise location of where proposal would take place (not coordinates)', max_length=200, blank=True, null=True)
    start_time_frame = models.CharField(help_text='Approximate date on which the proposed project is expected to start', max_length=100, blank=False, null=False)
    duration = models.CharField(help_text='Period of time expected that the proposed project will last', max_length=100, blank=False, null=False)
    applicant = models.ForeignKey(Person, help_text='Main applicant of the proposal', blank=False, null=False, on_delete=models.PROTECT)
    summary = models.TextField(help_text='Summary of the proposal submitted for funding', blank=False, null=False) # needs validator for max 400 words
    description = models.TextField(help_text='Outline of proposal', blank=False, null=False) # needs validator for max 1600 words
    requested_funds_explanation = models.TextField(help_text='Explanation about how proposed funds would be used', blank=False, null=False)
    logistics_requirements = models.TextField(help_text='Description of requirements regarding logistics and local partners', blank=False, null=False) # Check if this is a more specifc requirement for the exploratory grants call
    proposal_status = models.ForeignKey(ProposalStatus, help_text='Status or outcome of the proposal', blank=False, null=False, on_delete=models.PROTECT)

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


class BudgetItem(models.Model):
    """Itemised line in a budget, comprising of a category, full details and the amount"""
    category = models.ForeignKey(BudgetCategory, help_text='', blank=False, null=False, on_delete=models.PROTECT)
    details = models.TextField(help_text='', blank=False, null=False)
    amount = models.DecimalField(help_text='Cost of category item', decimal_places=2, max_digits=10, blank=False, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}: {}'.format(self.category, self.amount)


class ProposedBudgetItem(BudgetItem):
    """Itemised line in a budget as part of a proposal"""
    proposal = models.ForeignKey(Proposal, help_text='Proposal it which the budget item relates', on_delete=models.PROTECT)


class FundingStatus(models.Model):
    """Status of funding"""
    status = models.CharField(help_text='Name of the status', max_length=30, blank=False, null=False)
    description = models.CharField(help_text='Decsription of the status', max_length=100, blank=False, null=False)

    def __str__(self):
        return self.status


class FundingItem(models.Model):
    """Specific item of funding"""
    organisation = models.ForeignKey(Organisation, help_text='Name of organisation from which the funding is sourced', blank=False, null=False, on_delete=models.PROTECT)
    status = models.ForeignKey(FundingStatus, help_text='Status of the funding item',blank=False, null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(help_text='Amount given in funding', decimal_places=2, max_digits=10, blank=False, null=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} - {}: {}'.format(self.organisation, self.status, self.amount)


class ProposalFundingItem(FundingItem):
    """Specific item of funding for a proposal (referring to funding that has been sourced from elsewhere, rather than
    funding that would result from that proposal being accepted)"""
    proposal = models.ForeignKey(Proposal, help_text='Proposal for which the funding has been sourced', on_delete=models.PROTECT)
