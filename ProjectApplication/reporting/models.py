from django.db import models
from django.db.models import Q

from project_core.models import FundingInstrument


class FundingInstrumentYearMissingData(models.Model):
    class MissingDataType(models.TextChoices):
        CAREER_STAGE_PROPOSAL_APPLICANT = 'CAREER_STAGE_PROPOSAL_APPLICANT', 'Career Stage Proposal Applicant'
        CAREER_STAGE_FUNDED_PROJECT_PI = 'CAREER_STAGE_FUNDED_PROJECT_PI', 'Career Stage Funded Project PI'
        GENDER_PROPOSAL_APPLICANT = 'GENDER_PROPOSAL_APPLICANT', 'Gender Proposal Applicant'
        GENDER_FUNDED_PROJECT_PI = 'GENDER_FUNDED_PROJECT_PI', 'Gender Funded Project PI'
        PROPOSALS = 'PROPOSALS'
        PROJECTS = 'PROJECTS'

    funding_instrument = models.ForeignKey(FundingInstrument, on_delete=models.PROTECT, null=True, blank=True)
    finance_year = models.IntegerField(null=True, blank=True)
    missing_data_type = models.CharField(max_length=32, choices=MissingDataType.choices,
                                         blank=True, null=True)
    description = models.CharField(help_text='Reason that there is missing data. It might be shown in the management',
                                   max_length=128)

    @staticmethod
    def is_missing_data(missing_data_type, *, funding_instrument=None, year=None):
        if missing_data_type is None:
            return False, None

        rows = FundingInstrumentYearMissingData.objects.filter(
            Q(funding_instrument=funding_instrument) | Q(funding_instrument__isnull=True),
            Q(finance_year=year) | Q(finance_year__isnull=True),
            missing_data_type=missing_data_type, )

        if rows:
            return True, rows.first().description
        else:
            return False, None

    def __str__(self):
        funding_instrument = '*' if self.funding_instrument is None else self.funding_instrument
        finance_year = '*' if self.finance_year is None else self.finance_year

        return f'Funding Instrument: {funding_instrument} Year: {finance_year}'

    class Meta:
        verbose_name_plural = 'Funding Instrument Year Missing Data'
