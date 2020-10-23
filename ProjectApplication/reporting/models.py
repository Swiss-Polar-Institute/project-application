from django.db import models

from project_core.models import FundingInstrument


class FundingInstrumentYearMissingData(models.Model):
    funding_instrument = models.ForeignKey(FundingInstrument, on_delete=models.PROTECT)
    finance_year = models.IntegerField()
    description = models.CharField(help_text='Reason that there is missing data. It might be shown in the management',
                                   max_length=128)

    def __str__(self):
        return f'{self.funding_instrument}-{self.finance_year}'

    class Meta:
        verbose_name_plural = 'Funding Instrument Year Missing Data'
