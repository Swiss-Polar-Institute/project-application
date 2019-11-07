from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from project_core.forms.budget import BudgetItemFormSet
from project_core.forms.funding import ProposalFundingItemFormSet
from project_core.forms.partners import ProposalPartnersInlineFormSet
from project_core.forms.proposal import ProposalForm
from project_core.forms.datacollection import DataCollectionForm
from project_core.forms.person import PersonForm
from project_core.forms.questions import Questions
from project_core.models import Proposal, ProposalQAText, Call, ProposalStatus

PROPOSAL_FORM_NAME = 'proposal_form'
PERSON_FORM_NAME = 'person_form'
QUESTIONS_FORM_NAME = 'questions_form'
BUDGET_FORM_NAME = 'budget_form'
FUNDING_FORM_NAME = 'funding_form'
DATA_COLLECTION_FORM_NAME = 'data_collection_form'
PROPOSAL_PARTNERS_FORM_NAME = 'proposal_partners_form'


class AbstractProposalDetailView(TemplateView):
    template = ''

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        proposal = Proposal.objects.get(uuid=kwargs['uuid'])
        call = proposal.call

        context.update(call_context_for_template(call))

        context['proposal'] = proposal

        context['email'] = proposal.applicant.main_email()

        context['questions_answers'] = []

        for question in call.callquestion_set.all().order_by('order'):
            try:
                answer = ProposalQAText.objects.get(proposal=proposal, call_question=question).answer
            except ObjectDoesNotExist:
                answer = None

            question_text = question.question_text

            context['questions_answers'].append({'question': question_text,
                                                 'answer': answer})

        return render(request, self.template, context)


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
            questions_form = Questions(proposal=proposal,
                                       prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(proposal=proposal, prefix=BUDGET_FORM_NAME)

            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME,
                                                      instance=proposal)
            proposal_partners_form = ProposalPartnersInlineFormSet(prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                   instance=proposal)
            data_collection_form = DataCollectionForm(prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)

            context['proposal_action_url'] = reverse(self.action_url_update, kwargs={'uuid': proposal.uuid})

            context['action'] = 'Edit'

        else:
            call_pk = context['call_pk'] = request.GET.get('call')
            call = Call.objects.get(pk=call_pk)

            proposal_form = ProposalForm(call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(prefix=PERSON_FORM_NAME)
            questions_form = Questions(call=call,
                                       prefix=QUESTIONS_FORM_NAME)

            initial_budget = []
            for budget_category in call.budget_categories.all().order_by('order', 'name'):
                initial_budget.append({'category': budget_category, 'amount': None, 'details': None})

            budget_form = BudgetItemFormSet(call=call, prefix=BUDGET_FORM_NAME, initial=initial_budget)
            funding_form = ProposalFundingItemFormSet(prefix=FUNDING_FORM_NAME)
            proposal_partners_form = ProposalPartnersInlineFormSet(prefix=PROPOSAL_PARTNERS_FORM_NAME)
            data_collection_form = DataCollectionForm(prefix=DATA_COLLECTION_FORM_NAME)

            context['proposal_action_url'] = reverse(self.action_url_add)

            context['action'] = 'New'

        context.update(call_context_for_template(call))

        context[PROPOSAL_FORM_NAME] = proposal_form
        context[PERSON_FORM_NAME] = person_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form
        context[FUNDING_FORM_NAME] = funding_form
        context[PROPOSAL_PARTNERS_FORM_NAME] = proposal_partners_form
        context[DATA_COLLECTION_FORM_NAME] = data_collection_form

        return render(request, self.form_template, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # Optional form, depending on call.other_funding_question
        funding_form = proposal_partners_form = None

        if 'uuid' in kwargs:
            # Editing an existing proposal
            proposal_uuid = kwargs['uuid']
            proposal = Proposal.objects.get(uuid=proposal_uuid)
            call = proposal.call

            if timezone.now() > call.submission_deadline:
                return redirect(reverse('proposal-too-late') + '?action={}'.format('edited'))

        else:
            # New proposal
            call = Call.objects.get(id=int(request.POST['proposal_form-call_id']))

            if timezone.now() > call.submission_deadline:
                return redirect(reverse('proposal-too-late') + '?action={}'.format('edited'))

            proposal = None

        if proposal:
            # Editing an existing proposal
            proposal_form = ProposalForm(request.POST, instance=proposal, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, person_position=proposal.applicant, prefix=PERSON_FORM_NAME)
            questions_form = Questions(request.POST,
                                       proposal=proposal,
                                       prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, proposal=proposal, prefix=BUDGET_FORM_NAME)
            if call.other_funding_question:
                funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME,
                                                          instance=proposal)

            if call.proposal_partner_question:
                proposal_partners_form = ProposalPartnersInlineFormSet(request.POST, prefix=PROPOSAL_PARTNERS_FORM_NAME,
                                                                       instance=proposal)

            data_collection_form = DataCollectionForm(request.POST,
                                                      prefix=DATA_COLLECTION_FORM_NAME,
                                                      person_position=proposal.applicant)
            action = 'updated'

        else:
            # Creating a new proposal
            proposal_form = ProposalForm(request.POST, call=call, prefix=PROPOSAL_FORM_NAME)
            person_form = PersonForm(request.POST, prefix=PERSON_FORM_NAME)
            questions_form = Questions(request.POST,
                                       call=call,
                                       prefix=QUESTIONS_FORM_NAME)
            budget_form = BudgetItemFormSet(request.POST, call=call, prefix=BUDGET_FORM_NAME)

            if call.other_funding_question:
                funding_form = ProposalFundingItemFormSet(request.POST, prefix=FUNDING_FORM_NAME)

            if call.proposal_partner_question:
                proposal_partners_form = ProposalPartnersInlineFormSet(request.POST, prefix=PROPOSAL_PARTNERS_FORM_NAME)

            data_collection_form = DataCollectionForm(request.POST, prefix=DATA_COLLECTION_FORM_NAME)

            action = 'created'

        forms_to_validate = [person_form, proposal_form, questions_form, budget_form,
                             data_collection_form]

        if call.other_funding_question:
            forms_to_validate.append(funding_form)

        if call.proposal_partner_question:
            forms_to_validate.append(proposal_partners_form)

        all_valid = True
        for form in forms_to_validate:
            is_valid = form.is_valid()
            all_valid = all_valid and is_valid

        if all_valid:
            applicant = person_form.save_person()
            data_collection_form.update(applicant)

            proposal = proposal_form.save(commit=False)
            proposal.applicant = applicant
            proposal.proposal_status = ProposalStatus.objects.get(name='Submitted')
            proposal.save()
            proposal_form.save(commit=True)

            if call.other_funding_question:
                funding_form.save_fundings(proposal)

            questions_form.save_answers(proposal)
            budget_form.save_budgets(proposal)

            if call.proposal_partner_question:
                proposal_partners_form.save_partners(proposal)

            messages.success(request, self.success_message)

            return redirect(
                reverse(self.created_or_updated_url, kwargs={'uuid': proposal.uuid}) + '?action={}'.format(action))

        context[PERSON_FORM_NAME] = person_form
        context[PROPOSAL_FORM_NAME] = proposal_form
        context[QUESTIONS_FORM_NAME] = questions_form
        context[BUDGET_FORM_NAME] = budget_form

        if call.other_funding_question:
            context[FUNDING_FORM_NAME] = funding_form

        if call.proposal_partner_question:
            context[PROPOSAL_PARTNERS_FORM_NAME] = proposal_partners_form

        context[DATA_COLLECTION_FORM_NAME] = data_collection_form

        context['action'] = 'Edit'

        context.update(call_context_for_template(call))

        messages.error(request, 'Proposal not saved. Please correct the errors in the form and try again')

        return render(request, 'common/proposal-form.tmpl', context)


def call_context_for_template(call):
    context = {'maximum_budget': call.budget_maximum,
               'call_name': call.long_name,
               'call_introductory_message': call.introductory_message,
               'call_submission_deadline': call.submission_deadline,
               'other_funding_question': call.other_funding_question,
               'proposal_partner_question': call.proposal_partner_question}

    return context
