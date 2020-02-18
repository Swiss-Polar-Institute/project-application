from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from ProjectApplication import settings
from project_core.models import Call, Proposal
from project_core.utils import user_is_in_group_name


class Reviewer(models.Model):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    calls = models.ManyToManyField(Call, blank=True)

    def __str__(self):
        calls = ', '.join([str(call) for call in self.calls.all()])
        return f'R: {self.user} C: {calls}'

    @staticmethod
    def filter_proposals(proposals, user):
        if user_is_in_group_name(user, settings.REVIEWER_GROUP_NAME):
            try:
                reviewer = Reviewer.objects.get(user=user)
            except ObjectDoesNotExist:
                proposals = Proposal.objects.none()
                return proposals

            proposals = proposals.filter(call__in=reviewer.calls.all())

        return proposals


class ProposalEvaluation(models.Model):
    PANEL_RECOMENDATION_FUND = 'Fund'
    PANEL_RECOMENDATION_RESERVE = 'Reserve'
    PANEL_RECOMENDATION_DO_NOT_FUND = 'NotFund'

    PANEL_RECOMENDATION = (
        (PANEL_RECOMENDATION_FUND, 'Fund'),
        (PANEL_RECOMENDATION_RESERVE, 'Reserve'),
        (PANEL_RECOMENDATION_DO_NOT_FUND, 'Do not fund'),
    )

    BOARD_DECISION_FUND = 'Fund'
    BOARD_DECISION_DO_NOT_FUND = 'NotFund'

    BOARD_DECISION = (
        (BOARD_DECISION_FUND, 'Fund'),
        (BOARD_DECISION_DO_NOT_FUND, 'Not Fund'),
    )

    ELIGIBILITYNOTCHECKED = 'Eligibility not checked'
    ELIGIBLE = 'Eligible'
    NOTELIGIBLE = 'Not eligible'

    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT)

    final_mark = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    allocated_budget = models.DecimalField(help_text='Allocated budget', decimal_places=2, max_digits=10,
                                           validators=[MinValueValidator(0)], blank=True, null=True)

    panel_remarks = models.TextField(blank=True, null=True)
    feedback_to_applicant = models.TextField(blank=True, null=True)
    panel_recommendation = models.CharField(choices=PANEL_RECOMENDATION, max_length=7)
    board_decision = models.CharField(choices=BOARD_DECISION, max_length=7)
    decision_date = models.DateField(blank=True, null=True)
