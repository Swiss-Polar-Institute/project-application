from django.db import models


# Create your models here.


class Step(models.Model):
    """"""
    name = models.CharField(help_text='', max_length=60, blank=False, null=False)
    description = models.CharField(help_text='', max_length=200, blank=False, null=False)

    def __str__(self):
        return "{}".format(self.name)


class StepDate(models.Model):
    """Model containing a list of notable dates that are used throughout the application."""
    step = models.ForeignKey(Step, help_text='Name of step',max_length=128, null=False)
    date = models.DateTimeField(help_text='Date and time of notable date',max_length=64, null=False)

    def __str__(self):
        return "{} - {}".format(self.step, self.date)


class Message(models.Model):

    CALL_INTRODUCTORY_MESSAGE = 'CI'

    MESSAGES= (
        (CALL_INTRODUCTORY_MESSAGE, 'Call introductory message'),
    )

    message_type = models.CharField(help_text='', max_length=5, choices=MESSAGES, blank=False, null=False)
    message = models.TextField(help_text='')

    def __str__(self):
        return self.message


class BudgetCategory(models.Model):
    """"""
    name = models.CharField()
    description = models.CharField()
    
    def __str__(self):
        return self.name


class Call(models.Model):
    """Description of calls."""
    long_name = models.CharField(help_text='Full name of the call', max_length=200, blank=False, null=False)
    short_name = models.CharField(help_text='Short name or acronym of the call', max_length=60, blank=True, null=True)
    description = models.TextField(help_text='Description of the call that can be used to distinguish it from others', blank=False, null=False)
    introductory_message = models.TextField(help_text='Introductory text to the call for applicants', blank=True, null=True)
    call_open_date = models.DateTimeField(help_text='Date on which the call is opened', blank=False, null=False)
    submission_deadline = models.DateTimeField(help_text='Submission deadline of the call', blank=False, null=False)
    budget_categories = models.ManyToManyField(BudgetCategory, help_text='Categories required for the budget for a call')
    budget_maximum = models.DecimalField(help_text='Maximum amount that can be requested in the proposal budget', blank=False, null=False)

    def __str__(self):
        return self.long_name


class Keyword(models.Model):
    """Set of keywords used to describe the topic of a project, proposal, mission etc. """
    name = models.CharField(help_text='Name of a keyword', max_length=128, blank=False, null=False)
    description = models.CharField(help_text='Decsription of a keyword that should be used to distinguish it from another keyword', max_length=512, blank=False, null=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.description)


class ProposalStatus(models.Model):
    """Status options for a proposal model."""
    name = models.CharField(help_text='Name of the status of the proposal table', max_length=50, blank=False, null=False)
    description = models.CharField(help_text='Detailed description of the proposal status name', max_length=512, blank=False, null=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.description)


class PersonTitle(models.Model):
    """"""
    title = models.CharField()


class Country(models.Model):
    """"""
    name = models.CharField()


class Organisation(models.Model):
    """"""
    name = models.CharField()
    group = models.CharField()
    address = models.CharField()
    country = models.ForeignKey(Country)


class Person(models.Model):
    """Information about a person."""
    academic_title = models.ForeignKey(PersonTitle, help_text='Title of the person', blank=False, null=False)
    first_name = models.CharField(help_text='First name(s) of a person', max_length=100, blank=False, null=False)
    surname = models.CharField(help_text='Last name(s) of a person', max_length=100, blank=False, null=False)
    organisation = models.ManyToManyField(Organisation, help_text='Organisation(s) represented by the person', blank=False, null=False)

    def __str__(self):
        return "{} {} - {}".format(self.first_name, self.last_name, ", ".join(self.organisation.all()))


class GeographicArea(models.Model):
    """"""
    area = models.CharField()
    definition= models.CharField()


class Proposal(models.Model):
    """Proposal submitted for a call - not yet evaluated and therefore not yet a project."""
    title = models.CharField(help_text='Title of the proposal being submitted', max_length=1000, blank=False, null=False)
    keywords = models.ManyToManyField(Keyword, help_text='Keywords that describe the topic of the proposal', blank=False)
    geographical_area = models.ForeignKey(GeographicArea, help_text='Description of the geographical area covered by the proposal', max_length=200, blank=False, null=False)
    location = models.CharField(help_text='More precise location of where proposal would take place (not coordinates)', blank=True, null=True)
    start_time_frame = models.CharField(help_text='Approximate date on which the proposed project is expected to start', max_length=100, blank=False, null=False)
    duration = models.CharField(help_text='Period of time expected that the proposed project will last', max_length=100, blank=False, null=False)
    applicant = models.ForeignKey(Person, help_text='Main applicant of the proposal', blank=False, null=False, on_delete=models.PROTECT)
    summary = models.TextField(help_text='Summary of the proposal submitted for funding', blank=False, null=False) # needs validator for max 400 words
    description = models.TextField(help_text='Outline of proposal', blank=False, null=False) # needs validator for max 1600 words
    requested_funds_explanation = models.TextField(help_text='Explanation about how proposed funds would be used', blank=False, null=False)
    logistics_requirements = models.TextField(help_text='Description of requirements regarding logistics and local partners', blank=False, null=False) # Check if this is a more specifc requirement for the exploratory grants call
    proposal_status = models.ForeignKey(ProposalStatus, help_text='Status or outcome of the proposal', blank=False, null=False, on_delete=models.PROTECT)

    def __str__(self):
        return "{} - {}".format(self.title, self.applicant)

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
    """"""
    category = models.ForeignKey(BudgetCategory, help_text='', blank=False, null=False)
    details = models.TextField(help_text='', blank=False, null=False)
    amount = models.DecimalField(help_text='Cost of category item', decimal_places=2, blank=False, null=True)
    proposal = models.ForeignKey(Proposal, help_text='Proposal it which the budget item relates')


class FundingStatus(models.Model):
    """"""
    status = models.CharField()
    description = models.CharField()


class FundingItem(models.Model):
    """"""
    organisation = models.ForeignKey(Organisation, help_text='Name of organisation from which the funding is sourced', blank=False, null=False)
    status = models.ForeignKey(FundingStatus, help_text='Status of the funding item')
    amount = models.DecimalField(help_text='', decimal_places=2, blank=False, null=False)
    proposal = models.ForeignKey(Proposal, help_text='Proposal for which the funding has been sourced')
    
