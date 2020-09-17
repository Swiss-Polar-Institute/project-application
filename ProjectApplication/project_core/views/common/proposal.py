import logging
import mimetypes
import os

from botocore.exceptions import EndpointConnectionError
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from ProjectApplication import settings
from comments.utils import comments_attachments_forms
from project_core.forms.applicant_role import RoleDescriptionForm
from project_core.forms.budget import BudgetItemFormSet
from project_core.forms.datacollection import DataCollectionForm
from project_core.forms.funding import ProposalFundingItemFormSet
from project_core.forms.partners import ProposalPartnersInlineFormSet
from project_core.forms.person import PersonForm
from project_core.forms.postal_address import PostalAddressForm
from project_core.forms.project_overarching import ProjectOverarchingForm
from project_core.forms.proposal import ProposalForm
from project_core.forms.questions import Questions
from project_core.models import Proposal, ProposalQAText, Call, ProposalStatus, CallQuestion, ProposalQAFile
from variable_templates.utils import get_template_value_for_call

PROPOSAL_FORM_NAME = 'proposal_form'
PERSON_FORM_NAME = 'person_form'
POSTAL_ADDRESS_FORM_NAME = 'postal_address_form'
QUESTIONS_FORM_NAME = 'questions_form'
BUDGET_FORM_NAME = 'budget_form'
FUNDING_FORM_NAME = 'funding_form'
DATA_COLLECTION_FORM_NAME = 'data_collection_form'
PROPOSAL_PARTNERS_FORM_NAME = 'proposal_partners_form'
APPLICANT_ROLE_DESCRIPTION_FORM_NAME = 'applicant_role_description_form'
PROPOSAL_PROJECT_OVERARCHING_FORM_NAME = 'project_overarching_form'

logger = logging.getLogger('comments')


class AbstractProposalDetailView(TemplateView):
    template = ''

    def prepare_context(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'uuid' in kwargs:
            # Public requests are based on 'uuid'
            proposal = Proposal.objects.get(uuid=kwargs['uuid'])
        elif 'pk' in kwargs:
            # Logged requests (for the comments specially) are based on 'id'
            proposal = Proposal.objects.get(id=kwargs['pk'])
        else:
            assert False
        call = proposal.call

        context.update(call_context_for_template(call))

        context['proposal'] = proposal

        context['questions_answers'] = []

        for question in call.callquestion_set.filter(answer_type=CallQuestion.TEXT).order_by('order'):
            try:
                answer = ProposalQAText.objects.get(proposal=proposal, call_question=question).answer
            except ObjectDoesNotExist:
                answer = None

            question_text = question.question_text

            context['questions_answers'].append({'question': question_text,
                                                 'answer': answer})

        context['questions_files'] = []
        for question in call.callquestion_set.filter(answer_type=CallQuestion.FILE).order_by('order'):
            try:
                proposal_qa_file = ProposalQAFile.objects.get(proposal=proposal, call_question=question)
                filename = os.path.basename(proposal_qa_file.file.name)
                md5 = proposal_qa_file.md5
                human_file_size = proposal_qa_file.human_file_size()
                proposal_qa_file_id = proposal_qa_file.id

            except ObjectDoesNotExist:
                filename = None
                md5 = None
                human_file_size = None
                proposal_qa_file_id = None

            question_text = question.question_text

            context['questions_files'].append({'question': question_text,
                                               'proposal_qa_file_id': proposal_qa_file_id,
                                               'file': {'name': filename,
                                                        'md5': md5,
                                                        'size': human_file_size,
                                                        }})

        if request.user.groups.filter(name='logged').exists():
            href = description = None

            if proposal.status_is_draft():
                href = reverse('proposal-update', kwargs={'uuid': proposal.uuid})
                description = 'Link to draft proposal'
            elif proposal.status_is_submitted():
                href = reverse('proposal-detail', kwargs={'uuid': proposal.uuid})
                description = 'Link to view proposal'

            if href and description:
                context[
                    'link_to_edit_or_display'] = f'(<a href="{href}"><i class="fas fa-link"></i> {description}</a>)'

        context.update(comments_attachments_forms('logged-proposal-comment-add', proposal))

        return context

    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)
        return render(request, self.template, context)


def action_is_save_draft(post_vars):
    return 'save_draft' in post_vars


def action_is_submit(post_vars):
    return 'submit' in post_vars


def action_is_save(post_vars):
    return 'save_changes' in post_vars


class AbstractProposalView(TemplateView):
    created_or_updated_url = ''
    form_template = ''
    action_url_add = ''
    action_url_update = ''
    success_message = ''

    extra_context = {}

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self.extra_context)

        if 'uuid' in kwargs:
            proposal_uuid = kwargs['uuid']
            proposal: Proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME, instance=proposal)
            person_form = PersonForm(prefix=PERSON_FORM_NAME, person_position=proposal.applicant)
            postal_address_form = PostalAddressForm(prefix=POSTAL_ADDRESS_FORM_NAME, instance=proposal.postal_address)

            questions_form = Questions(proposal=proposal,
                                       prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)

            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME,
                                                      instance=proposal)
            applicant_role_description_form = RoleDescriptionForm(prefix=APPLICANT_ROLE_DESCRIPTION_FORM_NAME,
                                                                  instance=proposal.applicant_role_description,
                                                                  call=call)
            proposal_partners_form = ProposalPartnersInlineFormSet(prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                   instance=proposal,
                                                                   form_kwargs={'call': call})
            data_collection_form = DataCollectionForm(prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)
            overarching_form = ProjectOverarchingForm(prefix=PROPOSAL_PROJECT_OVERARCHING_FORM_NAME,
                                                      instance=proposal.overarching_project)
            context['proposal_action_url'] = reverse(self.action_url_update, kwargs={'uuid': proposal.uuid})

            context['action'] = 'Edit'

            context['proposal_status_is_draft'] = proposal.status_is_draft()

        else:
            if request.GET.get('call', None) is None:
                logger.warning(
                    f'NOTIFY: User tried to access to {request.build_absolute_uri()}: call parameter is missing')
                return redirect(reverse('call-list'))

            call_pk = context['call_pk'] = request.GET.get('call')

            try:
                call = Call.objects.get(pk=call_pk)
            except ObjectDoesNotExist:
                logger.warning(f'NOTIFY: User tried to access to {request.build_absolute_uri()}: call does not exist')
                messages.warning(request, 'This call does not exist. Please see the list of open calls below')
                return redirect(reverse('call-list'))

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(prefix=PERSON_FORM_NAME, only_basic_fields=False)
            postal_address_form = PostalAddressForm(prefix=POSTAL_ADDRESS_FORM_NAME)
            questions_form = Questions(call=call,
                                       prefix=QUESTIONS_FORM_NAME)

            initial_budget = []
            for budget_category in call.budget_categories.all().order_by('order', 'name'):
                initial_budget.append({'category': budget_category, 'amount': None, 'details': None})

            budget_form = BudgetItemFormSet(call=call, prefix=BUDGET_FORM_NAME, initial=initial_budget)
            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME)
            applicant_role_description_form = RoleDescriptionForm(prefix=APPLICANT_ROLE_DESCRIPTION_FORM_NAME,
                                                                  call=call)
            proposal_partners_form = ProposalPartnersInlineFormSet(prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                   form_kwargs={'call': call})
            overarching_form = ProjectOverarchingForm(prefix=PROPOSAL_PROJECT_OVERARCHING_FORM_NAME)
            data_collection_form = DataCollectionForm(prefix=DATA_COLLECTION_FORM_NAME)

            if getattr(self, 'preview', False):
                context['proposal_action_url'] = None
                context['preview'] = True
            else:
                context['proposal_action_url'] = f'{reverse(self.action_url_add)}?call={call.id}'

            context['action'] = 'New'

        context.update(call_context_for_template(call))

        context[PROPOSAL_FORM_NAME] = proposal_form
        context[POSTAL_ADDRESS_FORM_NAME] = postal_address_form
        context[PERSON_FORM_NAME] = person_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form
        context[FUNDING_FORM_NAME] = funding_form
        context[APPLICANT_ROLE_DESCRIPTION_FORM_NAME] = applicant_role_description_form
        context[PROPOSAL_PARTNERS_FORM_NAME] = proposal_partners_form
        context[DATA_COLLECTION_FORM_NAME] = data_collection_form
        context[PROPOSAL_PROJECT_OVERARCHING_FORM_NAME] = overarching_form

        context['activity'] = get_template_value_for_call('activity', call)

        if timezone.now() > call.submission_deadline:
            messages.error(request,
                           'New proposals for this call cannot be accepted because the submission deadline has now passed.')

        return render(request, self.form_template, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # Optional form, depending on call.other_funding_question
        funding_form = applicant_role_description_form = proposal_partners_form = proposal_project_overarching_form = None

        if 'uuid' in kwargs:
            # Editing an existing proposal
            proposal_uuid = kwargs['uuid']
            proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call

            if not request.user.groups.filter(name='management').exists():
                proposal_status = proposal.proposal_status
                proposal_status_draft = ProposalStatus.objects.get(name='Draft')

                if timezone.now() > call.submission_deadline:
                    if action_is_submit(request.POST) and proposal_status == proposal_status_draft:
                        messages.error(request,
                                       'The submission deadline has now passed. Your proposal cannot be submitted.')
                    elif action_is_submit(request.POST) and proposal_status != proposal_status_draft:
                        messages.error(request,
                                       'The submission deadline has now passed. Your submitted proposal can no longer be modified.')
                    else:
                        # The user pressed 'Save Draft'
                        messages.error(request,
                                       'The submission deadline has now passed. You cannot modify this proposal.')

                    return redirect(reverse('proposal-cannot-modify'))

                if proposal_status != proposal_status_draft:
                    # This is a user trying to modify a submitted proposal
                    messages.error(request,
                                   'Your proposal has already been submitted. It can no longer be edited.')
                    return redirect(reverse('proposal-cannot-modify'))

        else:
            # New proposal
            call = Call.objects.get(id=int(self.request.GET['call']))

            if timezone.now() > call.submission_deadline:
                messages.error(request,
                               'The submission deadline has now passed. Your proposal can no longer be submitted.')
                return redirect(reverse('proposal-cannot-modify'))

            proposal = None

        if proposal:
            # Editing an existing proposal
            proposal_form = ProposalForm(request.POST, instance=proposal, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, person_position=proposal.applicant, prefix=PERSON_FORM_NAME)
            postal_address_form = PostalAddressForm(request.POST, instance=proposal.postal_address,
                                                    prefix=POSTAL_ADDRESS_FORM_NAME)
            questions_form = Questions(request.POST,
                                       request.FILES,
                                       proposal=proposal,
                                       prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, proposal=proposal, prefix=BUDGET_FORM_NAME)
            if call.other_funding_question:
                funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME,
                                                          instance=proposal)

            if call.proposal_partner_question:
                applicant_role_description_form = RoleDescriptionForm(request.POST,
                                                                      prefix=APPLICANT_ROLE_DESCRIPTION_FORM_NAME,
                                                                      instance=proposal.applicant_role_description,
                                                                      call=call)
                proposal_partners_form = ProposalPartnersInlineFormSet(request.POST, prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                       instance=proposal,
                                                                       applicant_role_description_form=applicant_role_description_form,
                                                                       person_form=person_form,
                                                                       form_kwargs={
                                                                           'call': proposal.call})  # TODO exclude the values

            if call.overarching_project_question:
                proposal_project_overarching_form = ProjectOverarchingForm(request.POST,
                                                                           prefix=PROPOSAL_PROJECT_OVERARCHING_FORM_NAME,
                                                                           instance=proposal.overarching_project)

            data_collection_form = DataCollectionForm(request.POST,
                                                      prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)

        else:
            # Creating a new proposal
            proposal_form = ProposalForm(request.POST, call=call, prefix=PROPOSAL_FORM_NAME)
            postal_address_form = PostalAddressForm(request.POST, prefix=POSTAL_ADDRESS_FORM_NAME)
            person_form = PersonForm(request.POST, prefix=PERSON_FORM_NAME)
            questions_form = Questions(request.POST,
                                       request.FILES,
                                       call=call,
                                       prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, prefix=BUDGET_FORM_NAME)

            if call.other_funding_question:
                funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME)

            if call.proposal_partner_question:
                applicant_role_description_form = RoleDescriptionForm(request.POST,
                                                                      prefix=APPLICANT_ROLE_DESCRIPTION_FORM_NAME,
                                                                      call=call)
                proposal_partners_form = ProposalPartnersInlineFormSet(request.POST, prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                       applicant_role_description_form=applicant_role_description_form,
                                                                       person_form=person_form,
                                                                       form_kwargs={'call': call})

            if call.overarching_project_question:
                proposal_project_overarching_form = ProjectOverarchingForm(request.POST,
                                                                           prefix=PROPOSAL_PROJECT_OVERARCHING_FORM_NAME)

            data_collection_form = DataCollectionForm(request.POST, prefix=DATA_COLLECTION_FORM_NAME)

        forms_to_validate = [person_form, postal_address_form, proposal_form,
                             questions_form, budget_form, data_collection_form]

        if call.other_funding_question:
            forms_to_validate.append(funding_form)

        if call.proposal_partner_question:
            forms_to_validate.append(applicant_role_description_form)
            forms_to_validate.append(proposal_partners_form)

        if call.overarching_project_question:
            forms_to_validate.append(proposal_project_overarching_form)

        all_valid = True
        for form in forms_to_validate:
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        all_valid = all_valid and self._validate_project_title_applicant(proposal_form, person_form)

        if all_valid:
            proposal = proposal_form.save(commit=False)

            applicant = person_form.save_person()
            data_collection_form.update(applicant)

            proposal.applicant = applicant

            proposal_is_draft_or_submitted = False
            if action_is_save_draft(request.POST):
                proposal.proposal_status = ProposalStatus.objects.get(name='Draft')
                proposal_is_draft_or_submitted = True
            elif action_is_submit(request.POST):
                proposal.proposal_status = ProposalStatus.objects.get(name='Submitted')
                proposal_is_draft_or_submitted = True
            elif action_is_save(request.POST):
                pass
            else:
                assert False

            if not proposal_is_draft_or_submitted and not request.user.groups.filter(
                    name=settings.MANAGEMENT_GROUP_NAME).exists():
                return HttpResponseForbidden('Insufficient permissions to save the proposal with the selected status')

            if call.overarching_project_question:
                project_overarching = proposal_project_overarching_form.save()
                proposal.overarching_project = project_overarching

            postal_address = postal_address_form.save()

            proposal.postal_address = postal_address

            proposal.save()
            proposal_form.save(commit=True)

            if call.other_funding_question:
                funding_form.save_fundings(proposal)

            if not questions_form.save_answers(proposal):
                # The current only reason to fail is that the file cannot be saved
                # because of problems with the S3 storage
                messages.error(request,
                               'File attachments could not be saved - please try editing your proposal or contact SPI if this error reoccurs')

            budget_form.save_budgets(proposal)

            if call.proposal_partner_question:
                proposal.applicant_role_description = applicant_role_description_form.save()
                proposal.save()

                proposal_partners_form.save_partners(proposal)

            messages.success(request, self.success_message)

            return redirect(
                reverse(self.created_or_updated_url, kwargs={'uuid': proposal.uuid})
            )

        context[PERSON_FORM_NAME] = person_form
        context[POSTAL_ADDRESS_FORM_NAME] = postal_address_form
        context[PROPOSAL_FORM_NAME] = proposal_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form

        if call.other_funding_question:
            context[FUNDING_FORM_NAME] = funding_form

        if call.proposal_partner_question:
            context[APPLICANT_ROLE_DESCRIPTION_FORM_NAME] = applicant_role_description_form
            context[PROPOSAL_PARTNERS_FORM_NAME] = proposal_partners_form

        if call.overarching_project_question:
            context[PROPOSAL_PROJECT_OVERARCHING_FORM_NAME] = proposal_project_overarching_form

        context[DATA_COLLECTION_FORM_NAME] = data_collection_form

        context['activity'] = get_template_value_for_call('activity', call)

        context['action'] = 'Edit'

        context.update(call_context_for_template(call))

        messages.error(request, 'Proposal not saved. Please correct the errors in the form and try again.')

        return render(request, 'common/form-proposal.tmpl', context)

    def _validate_project_title_applicant(self, proposal_form, person_form):
        proposal_title = proposal_form.cleaned_data['title']
        call_id = proposal_form.cleaned_data['call_id']

        for person_position in person_form.get_person_positions():
            proposals = Proposal.objects.filter(title=proposal_title,
                                                applicant=person_position,
                                                call_id=call_id).exclude(id=proposal_form.instance.id)

            if len(proposals) > 0:
                proposal_form.raise_duplicated_title()
                return False

        return True


def call_context_for_template(call):
    context = {'maximum_budget': call.budget_maximum,
               'call_name': call.long_name,
               'call_introductory_message': call.introductory_message,
               'call_submission_deadline': call.submission_deadline,
               'other_funding_question': call.other_funding_question,
               'overarching_project_question': call.overarching_project_question,
               'proposal_partner_question': call.proposal_partner_question
               }

    return context


class ProposalQuestionAnswerFileView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        question_answer = ProposalQAFile.objects.get(id=kwargs['proposal_qa_file_id'], md5=kwargs['md5'])

        filename, file_extension = os.path.splitext(question_answer.file.name)

        content_type = mimetypes.types_map.get(file_extension.lower(), 'application/octet-stream')

        try:
            response = HttpResponse(
                question_answer.file.file.file,
                content_type=content_type
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(question_answer.file.name)
        except EndpointConnectionError:
            response = HttpResponse(content='Error: cannot connect to S3', content_type='text/plain')

        return response
