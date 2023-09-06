import storages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from simple_history.models import HistoricalRecords
from storages.backends.s3boto3 import S3Boto3Storage

from ProjectApplication import settings
from project_core.models import Call, Proposal, CreateModifyOn, ProposalStatus, PhysicalPerson, Project
from project_core.utils.utils import user_is_in_group_name


class Reviewer(models.Model):
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

            proposals = proposals.filter(call__in=reviewer.calls_without_closed_call_evaluation()). \
                filter(eligibility=Proposal.ELIGIBLE)

        return proposals

    def calls_without_closed_call_evaluation(self):
        return self.calls.filter(callevaluation__closed_date__isnull=True)

    def list_of_calls(self):
        calls = self.calls.all().order_by('short_name')
        return calls


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

    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT)

    allocated_budget = models.DecimalField(help_text='Allocated budget', decimal_places=2, max_digits=10,
                                           validators=[MinValueValidator(0)], blank=True, null=True)

    panel_remarks = models.TextField(help_text='Remarks made by the panel regarding the proposal', blank=True,
                                     null=True)
    feedback_to_applicant = models.TextField(help_text="Details of the panel's feedback to the applicant", blank=True,
                                             null=True)
    panel_recommendation = models.CharField(choices=PANEL_RECOMMENDATION, max_length=7,
                                            help_text='Recommendation made by the panel', blank=True, null=True)
    board_decision = models.CharField(choices=BOARD_DECISION, max_length=7, help_text='Decision made by the board',
                                      blank=True, null=True)
    decision_date = models.DateField(help_text="Date on which the board's decision was made", blank=True, null=True)
    decision_letter = models.FileField(storage=storages.backends.s3boto3.S3Boto3Storage(),
                                       upload_to=proposal_evaluation_eligibility_letter_rename,
                                       help_text='Decision letter file sent to applicant',
                                       blank=True, null=True)
    decision_letter_date = models.DateField(help_text='Date on which the decision letter was sent', blank=True,
                                            null=True)
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
            return 'Rejected'
        if self.board_decision == ProposalEvaluation.BOARD_DECISION_FUND:
            return 'Approved'

        return self.board_decision

    def board_decision_badge_class(self):
        lookup = {ProposalEvaluation.BOARD_DECISION_FUND: 'badge-success',
                  ProposalEvaluation.BOARD_DECISION_DO_NOT_FUND: 'badge-danger',
                  None: 'badge-secondary'}

        return lookup[self.board_decision]

    def comments(self):
        return self.proposalevaluationcomment_set.all().order_by('created_on')

    def can_edit(self):
        return self.proposal.call.callevaluation.is_open()

    def reason_cannot_edit(self):
        if not self.proposal.call.callevaluation.is_open():
            return 'Cannot edit proposal evaluation because call evaluation is closed'


def post_panel_management_table_rename(instance, filename):
    return f'evaluation/CallEvaluation/{instance.call.id}-{filename}'


class CallEvaluation(CreateModifyOn):
    call = models.OneToOneField(Call, on_delete=models.PROTECT)

    panel_date = models.DateField(help_text='Date on which the panel review meeting will take place')

    post_panel_management_table = models.FileField(storage=S3Boto3Storage(),
                                                   upload_to=post_panel_management_table_rename,
                                                   help_text='File in which the panel review information is contained',
                                                   blank=True, null=True)

    closed_date = models.DateTimeField(blank=True, null=True)
    closed_user = models.ForeignKey(User, help_text='User by which the Call Evaluation was closed',
                                    blank=True, null=True,
                                    on_delete=models.PROTECT)

    history = HistoricalRecords()

    def __str__(self):
        return f'CallEvaluation: {self.id} for call: {self.call.little_name()}'

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
        return []

    def is_closed(self):
        return self.closed_date is not None

    def is_open(self):
        return self.closed_date is None

    def close(self, user_closing_call_evaluation):
        """ It creates the projects and closes the call. """
        created_projects = []

        with transaction.atomic():
            for proposal in Proposal.objects.filter(call=self.call).filter(
                    proposalevaluation__board_decision=ProposalEvaluation.BOARD_DECISION_FUND).order_by('?'):
                project = Project.create_from_proposal(proposal, len(created_projects) + 1)

                created_projects.append(project)

            self.closed_date = timezone.now()
            self.closed_user = user_closing_call_evaluation
            self.save()

        return created_projects


def one_line_only(value):
    if isinstance(value, str) and '\n' in value:
        raise ValidationError('Only one line descriptions. It is used in a spreadsheet cell')


class Criterion(CreateModifyOn):
    name = models.CharField(max_length=128,
                            help_text='Name of the criteria such as "Originality of the project" or "Impact of the requested funding"',
                            unique=True)
    description = models.TextField(help_text='One line explanation of the criteria', validators=[one_line_only])

    class Meta:
        verbose_name_plural = 'Criteria'

    def __str__(self):
        return self.name


class CriterionCallEvaluation(CreateModifyOn):
    call_evaluation = models.ForeignKey(CallEvaluation,
                                        help_text='Call Evaluation that this Criterion is included in',
                                        on_delete=models.PROTECT)

    criterion = models.ForeignKey(Criterion,
                                  help_text='Call Evaluation Criterion that this is referred to',
                                  on_delete=models.PROTECT)

    enabled = models.BooleanField(help_text='Appears in the Call Evaluation', default=False)

    order = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('call_evaluation', 'criterion'),)
        verbose_name_plural = 'Criterion call evaluations'

    def __str__(self):
        return self.criterion.name
