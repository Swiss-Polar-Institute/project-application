import io
from io import BytesIO

import zipfile
import requests
from django.http import HttpResponse
from django.urls import reverse
from django.views import View


class ProposalDetailViewZip(View):
    def get(self, request, *args, **kwargs):
        proposal_uuid = kwargs['uuid']

        url = reverse('proposal-detail-pdf', kwargs={'uuid': proposal_uuid})
        url = request.build_absolute_uri(url)

        proposal_pdf_content = requests.get(url)

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip_archive:
            with zip_archive.open('proposal.pdf', mode='w') as pdf_proposal:
                pdf_proposal.write(proposal_pdf_content.content)

        filename = 'test.zip'

        response = HttpResponse(buffer.getvalue())
        response['Content-Type'] = 'application/x-zip-compressed'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
