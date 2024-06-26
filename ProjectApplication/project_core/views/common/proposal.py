import logging
import mimetypes
import os
import re

from botocore.exceptions import EndpointConnectionError
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from ProjectApplication import settings
from comments.utils import comments_attachments_forms
from evaluation.models import CallEvaluation
from project_core.forms.applicant_role import RoleDescriptionForm
from project_core.forms.budget import BudgetItemFormSet
from project_core.forms.budget_application import BudgetApplicationItemFormSet
from project_core.forms.datacollection import DataCollectionForm
from project_core.forms.funding import ProposalFundingItemFormSet
from project_core.forms.partners import ProposalPartnersInlineFormSet
from project_core.forms.person import PersonForm
from project_core.forms.person_application import PersonApplicationForm
from project_core.forms.postal_address import PostalAddressForm
from project_core.forms.postal_address_application import PostalAddressApplicationForm
from project_core.forms.project_overarching import ProjectOverarchingForm
from project_core.forms.proposal import ProposalForm
from project_core.forms.proposal_application import ProposalApplicationForm
from project_core.forms.scientific_clusters import ScientificClustersInlineFormSet
from project_core.models import Proposal, ProposalQAText, Call, ProposalStatus, ProposalQAFile, CallCareerStage
from project_core.views.common.proposal_parts import ProposalParts
from variable_templates.utils import get_template_value_for_call, apply_templates_to_string

PROPOSAL_FORM_NAME = 'proposal_form'
PROPOSAL_APPLICATION_FORM_NAME = 'proposal_application_form'
PERSON_FORM_NAME = 'person_form'
PERSON_APPLICATION_FORM_NAME = 'person_application_form'
POSTAL_ADDRESS_FORM_NAME = 'postal_address_form'
POSTAL_ADDRESS_APPLICATION_FORM_NAME = 'postal_address_application_form'
QUESTIONS_FORM_NAME = 'questions_form'
BUDGET_FORM_NAME = 'budget_form'
BUDGET_APPLICATION_FORM_NAME = 'budget_application_form'
FUNDING_FORM_NAME = 'funding_form'
DATA_COLLECTION_FORM_NAME = 'data_collection_form'
PROPOSAL_PARTNERS_FORM_NAME = 'proposal_partners_form'
APPLICANT_ROLE_DESCRIPTION_FORM_NAME = 'applicant_role_description_form'
PROPOSAL_PROJECT_OVERARCHING_FORM_NAME = 'project_overarching_form'
SCIENTIFIC_CLUSTERS_FORM_NAME = 'scientific_clusters_form'

logger = logging.getLogger('comments')


def _prepare_answers(call_questions, proposal):
    questions_answers = []
    for call_question in call_questions:
        try:
            answer = ProposalQAText.objects.get(proposal=proposal, call_question=call_question)
        except ObjectDoesNotExist:
            answer = None

        questions_answers.append(answer)

    return questions_answers


def get_parts_with_answers(proposal):
    parts = []

    for part in proposal.call.parts():
        questions_answers_text = _prepare_answers(part.questions_type_text(), proposal)
        questions_answers_file = _prepare_answers(part.questions_type_files(), proposal)

        parts.append({'title': apply_templates_to_string(part.title, proposal.call),
                      'introductory_text': apply_templates_to_string(part.introductory_text, proposal.call),
                      'heading_number': part.heading_number,
                      'questions_type_text': questions_answers_text,
                      'questions_type_file': questions_answers_file,
                      'div_id': part.div_id()
                      })

    return parts


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

        context['part_numbers'] = call.get_part_numbers_for_call()

        context['parts_with_answers'] = ProposalParts(request.POST, request.FILES, proposal, call).get_parts()

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

        update_files_enabled = not CallEvaluation.objects.filter(call=proposal.call).exists()
        context['update_files_enabled'] = update_files_enabled
        if update_files_enabled is False:
            context[
                'reason_update_files_disabled'] = 'Files cannot be changed because the evaluation has already started'

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


def get_number(string):
    # If string is a number: returns the number (as int)
    # If string is not a number but starts as a number: returns the number until the non-number part
    # If string does not start as a number: returns None
    # Examples: '2424' return 2424
    #           '13[0]' returns 13

    m = re.match('^([0-9]+)', string)

    if m:
        return int(m[1])

    return None


class AbstractProposalView(TemplateView):
    # TODO: Refactor this class and break up in parts
    # This is the longer, worse class in this project

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
            proposal_application_form = ProposalApplicationForm(call=call, prefix=PROPOSAL_APPLICATION_FORM_NAME, instance=proposal)
            person_form = PersonForm(prefix=PERSON_FORM_NAME,
                                     person_position=proposal.applicant,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            person_application_form = PersonApplicationForm(prefix=PERSON_APPLICATION_FORM_NAME,
                                     person_position=proposal.applicant,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            postal_address_form = PostalAddressForm(prefix=POSTAL_ADDRESS_FORM_NAME, instance=proposal.postal_address)
            postal_address_application_form = PostalAddressApplicationForm(prefix=POSTAL_ADDRESS_APPLICATION_FORM_NAME, instance=proposal.postal_address)
            scientific_clusters_form = ScientificClustersInlineFormSet(prefix=SCIENTIFIC_CLUSTERS_FORM_NAME,
                                                                       instance=proposal)
            budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)
            budget_application_form = BudgetApplicationItemFormSet(proposal=proposal, prefix=BUDGET_APPLICATION_FORM_NAME)

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

            context['extra_parts'] = ProposalParts(None, None, proposal).get_parts()

        else:
            if request.GET.get('call', None) is None:
                logger.warning(
                    f'NOTIFY: User tried to access to {request.build_absolute_uri()}: call parameter is missing')
                return redirect(reverse('call-list'))

            call_pk = context['call_pk'] = get_number(request.GET.get('call'))

            if call_pk is None:
                logger.warning(
                    f'NOTIFY: User tried to access to {request.build_absolute_uri()}: call expected to be a number')
                messages.warning(request, 'This call does not exist. Please see the list of open calls below')
                return redirect(reverse('call-list'))

            try:
                call = Call.objects.get(pk=call_pk)
            except ObjectDoesNotExist:
                logger.warning(
                    f'NOTIFY: User tried to access to {request.build_absolute_uri()}: call does not exist')
                messages.warning(request, 'This call does not exist. Please see the list of open calls below')
                return redirect(reverse('call-list'))

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME)
            proposal_application_form = ProposalApplicationForm(call=call, prefix=PROPOSAL_APPLICATION_FORM_NAME)
            person_form = PersonForm(prefix=PERSON_FORM_NAME,
                                     only_basic_fields=False,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            person_application_form = PersonApplicationForm(prefix=PERSON_APPLICATION_FORM_NAME,
                                     only_basic_fields=False,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            postal_address_form = PostalAddressForm(prefix=POSTAL_ADDRESS_FORM_NAME)
            postal_address_application_form = PostalAddressApplicationForm(prefix=POSTAL_ADDRESS_APPLICATION_FORM_NAME)
            scientific_clusters_form = ScientificClustersInlineFormSet(prefix=SCIENTIFIC_CLUSTERS_FORM_NAME)
            initial_budget = []
            for budget_category in call.budgetcategorycall_set.filter(enabled=True).order_by('order',
                                                                                             'budget_category__name'):
                initial_budget.append({'category': budget_category.budget_category, 'amount': None, 'details': None})

            budget_form = BudgetItemFormSet(call=call, prefix=BUDGET_FORM_NAME, initial=initial_budget)
            budget_application_form = BudgetApplicationItemFormSet(call=call, prefix=BUDGET_APPLICATION_FORM_NAME, initial=initial_budget)
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

            context['extra_parts'] = ProposalParts(None, None, proposal=None, call=call).get_parts()

        context.update(call_context_for_template(call))

        context[PROPOSAL_FORM_NAME] = proposal_form
        context[PROPOSAL_APPLICATION_FORM_NAME] = proposal_application_form
        context[POSTAL_ADDRESS_FORM_NAME] = postal_address_form
        context[POSTAL_ADDRESS_APPLICATION_FORM_NAME] = postal_address_application_form
        context[PERSON_FORM_NAME] = person_form
        context[PERSON_APPLICATION_FORM_NAME] = person_application_form
        context[SCIENTIFIC_CLUSTERS_FORM_NAME] = scientific_clusters_form
        context[BUDGET_FORM_NAME] = budget_form
        context[BUDGET_APPLICATION_FORM_NAME] = budget_application_form
        context[FUNDING_FORM_NAME] = funding_form
        context[APPLICANT_ROLE_DESCRIPTION_FORM_NAME] = applicant_role_description_form
        context[PROPOSAL_PARTNERS_FORM_NAME] = proposal_partners_form
        context[DATA_COLLECTION_FORM_NAME] = data_collection_form
        context[PROPOSAL_PROJECT_OVERARCHING_FORM_NAME] = overarching_form

        context['part_numbers'] = call.get_part_numbers_for_call()
        context['activity'] = get_template_value_for_call('activity', call)

        if timezone.now() > call.submission_deadline:
            messages.error(request,
                           'New proposals for this call cannot be accepted because the submission deadline has now passed.')

        return render(request, self.form_template, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # Optional form, depending on call.other_funding_question
        funding_form = applicant_role_description_form = proposal_partners_form = None
        proposal_project_overarching_form = scientific_clusters_form = budget_application_form = None

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

            career_stages = CallCareerStage.objects.filter(call=call)

            if timezone.now() > call.submission_deadline:
                messages.error(request,
                               'The submission deadline has now passed. Your proposal can no longer be submitted.')
                return redirect(reverse('proposal-cannot-modify'))

            proposal = None

        if proposal:
            # Editing an existing proposal
            proposal_form = ProposalApplicationForm(request.POST, instance=proposal, prefix=PROPOSAL_APPLICATION_FORM_NAME)
            person_form = PersonForm(request.POST, person_position=proposal.applicant,
                                     prefix=PERSON_FORM_NAME,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            person_application_form = PersonApplicationForm(request.POST, person_position=proposal.applicant,
                                     prefix=PERSON_APPLICATION_FORM_NAME,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            postal_address_application_form = PostalAddressApplicationForm(request.POST, instance=proposal.postal_address,
                                                    prefix=POSTAL_ADDRESS_APPLICATION_FORM_NAME)
            proposal_parts = ProposalParts(request.POST, request.FILES, proposal)

            if call.budget_requested_part():
                budget_application_form = BudgetApplicationItemFormSet(request.POST, call=call, proposal=proposal, prefix=BUDGET_APPLICATION_FORM_NAME)

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
                                                                       person_form=person_application_form,
                                                                       form_kwargs={
                                                                           'call': proposal.call})  # TODO exclude the values

            if call.overarching_project_question:
                proposal_project_overarching_form = ProjectOverarchingForm(request.POST,
                                                                           prefix=PROPOSAL_PROJECT_OVERARCHING_FORM_NAME,
                                                                           instance=proposal.overarching_project)

            if call.scientific_clusters_question:
                scientific_clusters_form = ScientificClustersInlineFormSet(request.POST, instance=proposal,
                                                                           prefix=SCIENTIFIC_CLUSTERS_FORM_NAME)

            data_collection_form = DataCollectionForm(request.POST,
                                                      prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)

        else:
            # Creating a new proposal
            proposal_form = ProposalApplicationForm(request.POST, call=call, prefix=PROPOSAL_APPLICATION_FORM_NAME)
            postal_address_application_form = PostalAddressApplicationForm(request.POST, prefix=POSTAL_ADDRESS_APPLICATION_FORM_NAME)

            proposal_parts = ProposalParts(request.POST, request.FILES, proposal=None, call=call)

            person_form = PersonForm(request.POST,
                                     prefix=PERSON_FORM_NAME,
                                     career_stages_queryset=call.enabled_career_stages_queryset())
            person_application_form = PersonApplicationForm(request.POST,
                                     prefix=PERSON_APPLICATION_FORM_NAME,
                                     career_stages_queryset=call.enabled_career_stages_queryset())

            if call.budget_requested_part():
                budget_application_form = BudgetApplicationItemFormSet(request.POST, call=call, prefix=BUDGET_APPLICATION_FORM_NAME)

            if call.other_funding_question:
                funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME)

            if call.proposal_partner_question:
                applicant_role_description_form = RoleDescriptionForm(request.POST,
                                                                      prefix=APPLICANT_ROLE_DESCRIPTION_FORM_NAME,
                                                                      call=call)
                proposal_partners_form = ProposalPartnersInlineFormSet(request.POST, prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                       applicant_role_description_form=applicant_role_description_form,
                                                                       person_form=person_application_form,
                                                                       form_kwargs={'call': call})

            if call.overarching_project_question:
                proposal_project_overarching_form = ProjectOverarchingForm(request.POST,
                                                                           prefix=PROPOSAL_PROJECT_OVERARCHING_FORM_NAME)

            if call.scientific_clusters_question:
                scientific_clusters_form = ScientificClustersInlineFormSet(request.POST,
                                                                           prefix=SCIENTIFIC_CLUSTERS_FORM_NAME)

            data_collection_form = DataCollectionForm(request.POST, prefix=DATA_COLLECTION_FORM_NAME)


        forms_to_validate = [person_application_form, postal_address_application_form, proposal_form]

        if call.other_funding_question:
            forms_to_validate.append(funding_form)

        if call.proposal_partner_question:
            forms_to_validate.append(applicant_role_description_form)
            forms_to_validate.append(proposal_partners_form)

        if call.overarching_project_question:
            forms_to_validate.append(proposal_project_overarching_form)

        if call.scientific_clusters_question:
            forms_to_validate.append(scientific_clusters_form)

        if call.budget_requested_part():
            forms_to_validate.append(budget_application_form)

        all_valid = True
        for form in forms_to_validate:
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        # all_valid = all_valid and self._validate_project_title_applicant(proposal_form, person_form)

        if all_valid:
            proposal = proposal_form.save(commit=False)

            applicant = person_application_form.save_person()
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

            postal_address = postal_address_application_form.save()

            proposal.postal_address = postal_address

            proposal.save()
            proposal_form.save(commit=True)

            if call.other_funding_question:
                funding_form.save_fundings(proposal)

            for question_form in proposal_parts.get_forms():
                if not question_form.save_answers(proposal):
                    messages.error(request,
                                   'File attachments could not be saved - please try attaching the files again or contact SPI if this error reoccurs')

            if call.budget_requested_part():
                budget_application_form.save_budgets(proposal)

            if call.proposal_partner_question:
                proposal.applicant_role_description = applicant_role_description_form.save()
                proposal.save()

                proposal_partners_form.save_partners(proposal)

            if call.scientific_clusters_question:
                scientific_clusters_form = ScientificClustersInlineFormSet(request.POST,
                                                                           instance=proposal,
                                                                           prefix=SCIENTIFIC_CLUSTERS_FORM_NAME)
                scientific_clusters_form.save()

            messages.success(request, self.success_message)

            return redirect(
                reverse(self.created_or_updated_url, kwargs={'uuid': proposal.uuid})
            )

        context[PERSON_FORM_NAME] = person_application_form
        context[PERSON_APPLICATION_FORM_NAME] = person_application_form
        context[POSTAL_ADDRESS_APPLICATION_FORM_NAME] = postal_address_application_form
        context[PROPOSAL_FORM_NAME] = proposal_form
        context[PROPOSAL_APPLICATION_FORM_NAME] = proposal_form
        for question_form in proposal_parts.get_forms():
            context[question_form.prefix] = question_form

        if call.other_funding_question:
            context[FUNDING_FORM_NAME] = funding_form

        if call.proposal_partner_question:
            context[APPLICANT_ROLE_DESCRIPTION_FORM_NAME] = applicant_role_description_form
            context[PROPOSAL_PARTNERS_FORM_NAME] = proposal_partners_form

        if call.overarching_project_question:
            context[PROPOSAL_PROJECT_OVERARCHING_FORM_NAME] = proposal_project_overarching_form

        if call.scientific_clusters_question:
            context[SCIENTIFIC_CLUSTERS_FORM_NAME] = scientific_clusters_form

        if call.budget_requested_part():
            context[BUDGET_APPLICATION_FORM_NAME] = budget_application_form

        context[DATA_COLLECTION_FORM_NAME] = data_collection_form

        context['activity'] = get_template_value_for_call('activity', call)

        context['action'] = 'Edit'

        context['part_numbers'] = call.get_part_numbers_for_call()

        context['extra_parts'] = proposal_parts.get_parts()

        context.update(call_context_for_template(call))

        messages.error(request, 'Proposal not saved. Please correct the errors in the form and try again.')

        return render(request, 'common/form-proposal.tmpl', context)

    # def _validate_project_title_applicant(self, proposal_form, person_form):
    #     proposal_title = proposal_form.data.get('title')
    #     call_id = proposal_form.data.get('call_id')
    #
    #     for person_position in person_form.get_person_positions():
    #         proposals = Proposal.objects.filter(title=proposal_title,
    #                                             applicant=person_position,
    #                                             call_id=call_id).exclude(id=proposal_form.instance.id)
    #
    #         if len(proposals) > 0:
    #             proposal_form.raise_duplicated_title()
    #             return False
    #
    #     return True


def check_duplicate_proposal(request):
    proposal_title = request.GET.get('proposal_title')
    call_id = request.GET.get('call_id')

    exists = Proposal.objects.filter(
        title=proposal_title,
        call_id=call_id
    ).exists()

    return JsonResponse({'exists': exists})

def call_context_for_template(call):
    context = {'maximum_budget': call.budget_maximum,
               'call_name': call.long_name,
               'call_introductory_message': call.introductory_message,
               'call_submission_deadline': call.submission_deadline,
               'other_funding_question': call.other_funding_question,
               'overarching_project_question': call.overarching_project_question,
               'scientific_clusters_question': call.scientific_clusters_question,
               'proposal_partner_question': call.proposal_partner_question,
               'budget_part': call.budget_requested_part()
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
