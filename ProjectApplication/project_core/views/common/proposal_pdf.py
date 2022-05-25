import logging
import subprocess
import pdfkit
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views import View

from project_core.models import Proposal

logger = logging.getLogger('project_core')


def create_pdf_for_proposal(proposal, request):
    url = reverse('proposal-detail', kwargs={'uuid': proposal.uuid})
    url = request.build_absolute_uri(url)

    if url.startswith('http://testserver/'):
        url = url.replace('http://testserver/', 'http://localhost:9998/', 1)

    command = ['wkhtmltopdf', '--quiet']

    if settings.SELF_HTTP_USERNAME:
        command += ['--username', settings.SELF_HTTP_USERNAME, '--password', settings.SELF_HTTP_PASSWORD]

    command += [url, '-']

    process = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    if process.returncode != 0:
        logger.warning(f'NOTIFY: PDF generation warning for {proposal.pk}: {process.stderr}')

    return process.stdout


class ProposalDetailViewPdf(View):
    def get(self, request, *args, **kwargs):
        proposal = Proposal.objects.get(uuid=kwargs['uuid'])
        url = reverse('proposal-detail', kwargs={'uuid': proposal.uuid})
        url = request.build_absolute_uri(url)

        if url.startswith('http://testserver/'):
            url = url.replace('http://testserver/', 'http://localhost:9998/', 1)

        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.95in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'minimum-font-size': "12"
        }

        proposal_pdf = pdfkit.from_url(url, options=options, verbose=True)

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = f'attachment; filename="{proposal.file_name()}.pdf'

        response.write(proposal_pdf)

        return response
