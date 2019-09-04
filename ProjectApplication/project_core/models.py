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
    long_name = models.CharField(help_text="Full name of the call", max_length=128, blank=False, null=False)
    short_name = models.CharField(help_text="Short name or acronym of the call", max_length=64, blank=True, null=True)
    description = models.TextField(help_text="Description of the call that can be used to distinguish it from others", blank=False, null=False)
    dates = models.ManyToManyField(Date, help_text="Notable date related to the call", blank=False)

    def __str__(self):
        return "{}".format(self.long_name)


