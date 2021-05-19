import subprocess

from django.http import HttpResponse
from django.urls import reverse
from django.views import View

from project_core.models import Proposal


class ProposalDetailViewPdf(View):
    def get(self, request, *args, **kwargs):
        proposal_uuid = kwargs['uuid']
        url = reverse('proposal-detail', kwargs={'uuid': proposal_uuid})
        url = request.build_absolute_uri(url)

        proposal = Proposal.objects.get(uuid=proposal_uuid)

        process = subprocess.run(['wkhtmltopdf', '--quiet', url, '-'], stdout=subprocess.PIPE)

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = f'attachment; filename="{proposal.file_name("pdf")}'

        response.write(process.stdout)

        return response
