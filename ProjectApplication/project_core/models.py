from django.db import models


# Create your models here.

class Date(models.Model):
    """Model containing a list of notable dates that are used throughout the application."""
    notable_date = models.CharField(help_text="Description of notable date",max_length=128, null=False)
    date = models.DateTimeField(help_text="Date and time of notable date",max_length=64, null=False)

    def __str__(self):
        return "{} - {}".format(self.notable_date, self.date)


class Call(models.Model):
    """Description of calls."""
    long_name = models.CharField(help_text="Full name of the call", max_length=200, blank=False, null=False)
    short_name = models.CharField(help_text="Short name or acronym of the call", max_length=60, blank=True, null=True)
    description = models.TextField(help_text="Description of the call that can be used to distinguish it from others", blank=False, null=False)
    dates = models.ManyToManyField(Date, help_text="Notable date related to the call", blank=False)

    def __str__(self):
        return "{}".format(self.long_name)


class Keyword(models.Model):
    """Set of keywords used to describe the topic of a project, proposal, mission etc. """
    name = models.CharField(help_text="Name of a keyword", max_length=128, blank=False, null=False)
    description = models.CharField(help_text="Decsription of a keyword that should be used to distinguish it from another keyword", max_length=512, blank=False, null=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.description)


class ProposalStatus(models.Model):
    """Status options for a proposal model."""
    name = models.CharField(help_text="Name of the status of the proposal table", max_length=50, blank=False, null=False)
    description = models.CharField(help_text="Detailed description of the proposal status name", max_length=512, blank=False, null=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.description)


class Person(models.Model):
    """Information about a person."""
    title = models.ForeignKey(PersonTitle, help_text="Title of the person", blank=False, null=False)
    first_name = models.CharField(help_text="First name(s) of a person", max_length=100, blank=False, null=False)
    last_name = models.CharField(help_text="Last name(s) of a person", max_length=100, blank=False, null=False)
    organisation = models.ManyToManyField(Organisation, help_text="Organisation(s) represented by the person", blank=False, null=False)

    def __str__(self):
        return "{} {} - {}".format(self.first_name, self.last_name, ", ".join(self.organisation.all()))


class Proposal(models.Model):
    """Proposal submitted for a call - not yet evaluated and therefore not yet a project."""
    title = models.CharField(help_text="Title of the proposal being submitted", max_length=1000, blank=False, null=False)
    keywords = models.ManyToManyField(Keyword, help_text="Keywords that describe the topic of the proposal", blank=False)
    geographical_area = models.TextField(help_text="Description of the geographical area covered by the proposal", max_length=200, blank=False, null=False)
    start_time_frame = models.TextField(help_text="Approximate date on which the proposed project is expected to start", blank=False, null=False)
    duration = models.TextField(help_text="Period of time expected that the proposed project will last", blank=False, null=False)
    requested_budget = models.FloatField(help_text="Total amount requested for proposal budget", blank=False, null=False)
    applicant = models.ForeignKey(Person, help_text="Main applicant of the proposal", blank=False, null=False, on_delete=models.PROTECT)
    proposal_status = models.ForeignKey(ProposalStatus, help_text="Status or outcome of the proposal", blank=False, null=False, on_delete=models.PROTECT)

    def __str__(self):
        return "{} - {}".format(self.title, self.applicant)

