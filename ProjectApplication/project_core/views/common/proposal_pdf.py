import os.path
import subprocess

from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import reverse
from xhtml2pdf import pisa

from ProjectApplication import settings
from project_core.models import Proposal
from project_core.views.common.proposal import AbstractProposalDetailView


def link_callback(uri, relative):
    if uri.startswith('http://') or uri.startswith('https://'):
        return uri
    elif uri.startswith(settings.STATIC_URL):
        resolved = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
        return resolved
    else:
        assert False, f'Unknown URI: {uri}'


class ProposalDetailViewPdf(AbstractProposalDetailView):
    template = 'external/proposal-detail.tmpl'

    def get(self, request, *args, **kwargs):
        proposal_uuid = kwargs['uuid']
        url = reverse('proposal-detail', kwargs={'uuid': proposal_uuid})
        url = request.build_absolute_uri(url)

        proposal = Proposal.objects.get(uuid=proposal_uuid)

        process = subprocess.run(['wkhtmltopdf', '--quiet', url, '-'], stdout=subprocess.PIPE)

        response = HttpResponse(content_type='application/pdf')

        # TODO: Names with umlauts, accents, etc. are going to cause a problem?
        applicant_full_name = proposal.applicant.person.full_name()
        filename = f'Proposal-{proposal.call.short_name}-{applicant_full_name}'
        filename = filename.replace(' ', '_').replace('.', '_')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        response.write(process.stdout)

        return response
