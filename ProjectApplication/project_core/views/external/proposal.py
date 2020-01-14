import textwrap

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic import TemplateView

from project_core.models import Proposal
from project_core.views.common.proposal import AbstractProposalDetailView, AbstractProposalView


def send_email_proposal_received(uuid, display_url, update_url):
    proposal = Proposal.objects.get(uuid=uuid)

    if not proposal.draft_saved_mail_sent or not proposal.submitted_mail_sent:
        recipient_list = [proposal.applicant.main_email()]

        footer = textwrap.dedent('''\
            Thank you for your interest. The SPI team remains at your disposal for questions at spi-grants@epfl.ch
            Please note that this email is sent from an unmonitored email address.
            ''')

        if proposal.status_is_draft() and not proposal.draft_saved_mail_sent:
            call_deadline = proposal.call.submission_deadline.strftime('%A %d %B %Y at %H:%M Swiss time')

            subject = 'Swiss Polar Institute - Proposal draft saved'
            body = textwrap.dedent(f'''\
                Your proposal: "{proposal.title}" for the call {proposal.call.long_name} has been saved.
                
                To edit it go to: {update_url} .
                Please note that when saving future drafts you will not receive another email confirmation.
                
                Please remember to submit your proposal before the call deadline: {call_deadline}.
                
                ''')

            body += footer

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient_list)
            proposal.draft_saved_mail_sent = True
            proposal.save()

        if proposal.status_is_submitted() and not proposal.submitted_mail_sent:
            subject = 'Swiss Polar Institute - Proposal submitted'
            body = textwrap.dedent(f'''\
                Thank you for submitting your proposal: "{proposal.title}" for the call {proposal.call.long_name}.
                
                You can view your submitted proposal here: {display_url} .
                                
                ''')

            body += footer

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient_list)
            proposal.submitted_mail_sent = True
            proposal.save()


class ProposalThankYouView(TemplateView):
    template_name = 'external/proposal-thank_you.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        uuid = kwargs['uuid']

        context['proposal'] = Proposal.objects.get(uuid=kwargs['uuid'])

        context['display_url'] = display_url = self.request.build_absolute_uri(
            reverse('proposal-detail', kwargs={'uuid': uuid}))

        context['update_url'] = update_url = self.request.build_absolute_uri(
            reverse('proposal-update', kwargs={'uuid': uuid}))

        send_email_proposal_received(uuid, display_url, update_url)

        return context


class ProposalCannotModify(TemplateView):
    template_name = 'external/proposal-cannot_modify.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProposalDetailView(AbstractProposalDetailView):
    template = 'external/proposal-detail.tmpl'


class ProposalView(AbstractProposalView):
    created_or_updated_url = 'proposal-thank-you'
    form_template = 'common/proposal-form.tmpl'
    action_url_update = 'proposal-update'
    action_url_add = 'proposal-add'
