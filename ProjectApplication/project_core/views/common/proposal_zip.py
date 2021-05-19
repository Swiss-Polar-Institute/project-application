import io
from io import BytesIO

import zipfile
import requests
from django.http import HttpResponse
from django.urls import reverse
from django.views import View

from project_core.models import Proposal


class ProposalDetailViewZip(View):
    def get(self, request, *args, **kwargs):
        proposal = Proposal.objects.get(uuid=kwargs['uuid'])

        url = reverse('proposal-detail-pdf', kwargs={'uuid': proposal.uuid})
        url = request.build_absolute_uri(url)

        proposal_pdf_content = requests.get(url)

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip_archive:
            with zip_archive.open(proposal.file_name('pdf'), mode='w') as pdf_proposal:
                pdf_proposal.write(proposal_pdf_content.content)

            for answer_file in proposal.proposalqafile_set.all():
                filename = answer_file.file_name()
                with zip_archive.open(filename, mode='w') as file_pointer:
                    file_pointer.write(answer_file.file.read())

        filename = proposal.file_name('zip')

        response = HttpResponse(buffer.getvalue())
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
