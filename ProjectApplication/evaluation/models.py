import storages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from simple_history.models import HistoricalRecords
from storages.backends.s3boto3 import S3Boto3Storage

from ProjectApplication import settings
from project_core.models import Call, Proposal, CreateModifyOn, ProposalStatus, PhysicalPerson, Project
from project_core.utils.utils import user_is_in_group_name


class Reviewer(models.Model):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    person = models.OneToOneField(PhysicalPerson, null=True, on_delete=models.PROTECT)
    calls = models.ManyToManyField(Call, blank=True)
    proposals = models.ManyToManyField(Proposal, blank=True)

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

            proposals = proposals.filter(call__in=reviewer.calls.all()).filter(eligibility=Proposal.ELIGIBLE)

        return proposals


def proposal_evaluation_eligibility_letter_rename(instance, filename):
    return f'evaluation/ProposalEvaluation/Proposal-{instance.proposal.id}-{filename}'


class ProposalEvaluation(CreateModifyOn):
    PANEL_RECOMMENDATION_FUND = 'Fund'
    PANEL_RECOMMENDATION_RESERVE = 'Reserve'
    PANEL_RECOMMENDATION_DO_NOT_FUND = 'NotFund'

    PANEL_RECOMMENDATION = (
        (PANEL_RECOMMENDATION_FUND, 'Fund'),
        (PANEL_RECOMMENDATION_RESERVE, 'Reserve'),
        (PANEL_RECOMMENDATION_DO_NOT_FUND, 'Do not fund'),
    )

    BOARD_DECISION_FUND = 'Fund'
    BOARD_DECISION_DO_NOT_FUND = 'NotFund'

    BOARD_DECISION = (
        (BOARD_DECISION_FUND, 'Fund'),
        (BOARD_DECISION_DO_NOT_FUND, 'Do not fund'),
    )

    ELIGIBILITYNOTCHECKED = 'Eligibility not checked'
    ELIGIBLE = 'Eligible'
    NOTELIGIBLE = 'Not eligible'

    objects = models.Manager()  # Helps Pycharm CE auto-completion

    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT)

    allocated_budget = models.DecimalField(help_text='Allocated budget', decimal_places=2, max_digits=10,
                                           validators=[MinValueValidator(0)], blank=True, null=True)

    panel_remarks = models.TextField(blank=True, null=True)
    feedback_to_applicant = models.TextField(blank=True, null=True)
    panel_recommendation = models.CharField(choices=PANEL_RECOMMENDATION, max_length=7, blank=True, null=True)
    board_decision = models.CharField(choices=BOARD_DECISION, max_length=7, blank=True, null=True)
    decision_date = models.DateField(blank=True, null=True)
    decision_letter = models.FileField(storage=storages.backends.s3boto3.S3Boto3Storage(),
                                       upload_to=proposal_evaluation_eligibility_letter_rename,
                                       blank=True, null=True)
    decision_letter_date = models.DateField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.proposal} Recommendation: {self.panel_recommendation}-{self.board_decision}'

    @staticmethod
    def comment_object():
        from comments.models import ProposalEvaluationComment
        return ProposalEvaluationComment

    @staticmethod
    def attachment_object():
        from comments.models import ProposalEvaluationAttachment
        return ProposalEvaluationAttachment

    def attachments(self):
        return self.proposalevaluationattachment_set.all().order_by('created_on')

    def panel_recommendation_str(self):
        if self.panel_recommendation == ProposalEvaluation.BOARD_DECISION_DO_NOT_FUND:
            return 'Do not fund'

        return self.panel_recommendation

    def panel_recommendation_badge_class(self):
        lookup = {ProposalEvaluation.PANEL_RECOMMENDATION_FUND: 'badge-success',
                  ProposalEvaluation.PANEL_RECOMMENDATION_RESERVE: 'badge-warning',
                  ProposalEvaluation.PANEL_RECOMMENDATION_DO_NOT_FUND: 'badge-danger',
                  None: 'badge-secondary'}

        return lookup[self.panel_recommendation]

    def board_decision_str(self):
        if self.board_decision == ProposalEvaluation.BOARD_DECISION_DO_NOT_FUND:
            return 'Do not fund'

        return self.board_decision

    def board_decision_badge_class(self):
        lookup = {ProposalEvaluation.BOARD_DECISION_FUND: 'badge-success',
                  ProposalEvaluation.BOARD_DECISION_DO_NOT_FUND: 'badge-danger',
                  None: 'badge-secondary'}

        return lookup[self.board_decision]

    def comments(self):
        return self.proposalevaluationcomment_set.all().order_by('created_on')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


def post_panel_management_table_rename(instance, filename):
    return f'evaluation/CallEvaluation/{instance.call.id}-{filename}'


class CallEvaluation(CreateModifyOn):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    call = models.OneToOneField(Call, on_delete=models.PROTECT)

    panel_date = models.DateField()

    post_panel_management_table = models.FileField(storage=S3Boto3Storage(),
                                                   upload_to=post_panel_management_table_rename,
                                                   blank=True, null=True)

    closed_date = models.DateTimeField(blank=True, null=True)
    closed_user = models.ForeignKey(User, help_text='User by which the Call Evaluation was closed',
                                    blank=True, null=True,
                                    on_delete=models.PROTECT)
    history = HistoricalRecords()

    @staticmethod
    def comment_object():
        from comments.models import CallEvaluationComment
        return CallEvaluationComment

    @staticmethod
    def attachment_object():
        return None

    def comments(self):
        return self.callevaluationcomment_set.all().order_by('created_on')

    def attachments(self):
        return None

    def __str__(self):
        return f'CallEvaluation: {self.id} for call: {self.call.little_name()}'

    def is_closed(self):
        return self.closed_date is not None

    def close(self, user_closing_call_evaluation):
        """ It creates the projects and closes the call. """
        created_projects = 0

        with transaction.atomic():
            for proposal in Proposal.objects.filter(call=self.call).filter(
                    proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_FUND).order_by('?'):
                Project.create_from_proposal(proposal, created_projects + 1)

                created_projects += 1

            self.closed_date = timezone.now()
            self.closed_user = user_closing_call_evaluation
            self.save()

        return created_projects
