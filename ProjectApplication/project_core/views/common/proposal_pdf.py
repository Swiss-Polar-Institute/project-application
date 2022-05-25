import logging
import pdfkit
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

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.95in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'minimum-font-size': "12"
    }

    return pdfkit.from_url(url, options=options, verbose=True)


class ProposalDetailViewPdf(View):
    def get(self, request, *args, **kwargs):
        proposal = Proposal.objects.get(uuid=kwargs['uuid'])

        proposal_pdf = create_pdf_for_proposal(proposal, request)

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = f'attachment; filename="{proposal.file_name()}.pdf'

        response.write(proposal_pdf)

        return response
