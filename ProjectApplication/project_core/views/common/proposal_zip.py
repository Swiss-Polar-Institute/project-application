import io
import os
import zipfile

from django.http import HttpResponse
from django.views import View

from project_core.models import Proposal
from project_core.views.common.proposal_pdf import create_pdf_for_proposal


def add_proposal_to_zip(proposal, zip_archive, request, used_directory_names):
    # Returns the directory name used for this proposal
    proposal_directory = initial_directory = proposal.file_name()

    count = 2
    while proposal_directory in used_directory_names:
        proposal_directory = f'{initial_directory}-{count}'
        count += 1

    proposal_filename = f'Proposal-{proposal.file_name()}.pdf'

    with zip_archive.open(os.path.join(proposal_directory, proposal_filename), mode='w') as pdf_proposal:
        proposal_pdf_content = create_pdf_for_proposal(proposal, request)

        pdf_proposal.write(proposal_pdf_content)

    for answer_file in proposal.proposalqafile_set.all():
        filename = answer_file.file_name()
        try:
            file_contents = answer_file.file.read()
        except OSError:
            file_contents = f'ERROR reading file from SPI object storage. File id: {answer_file.id} ' \
                            f'file name: {answer_file.file.name} file_md5: {answer_file.md5}'.encode('utf-8')
            filename = filename + '.txt'

        with zip_archive.open(os.path.join(proposal_directory, filename), mode='w') as file_pointer:
            file_pointer.write(file_contents)

    return proposal_directory


class ProposalDetailViewZip(View):
    def get(self, request, *args, **kwargs):
        proposal = Proposal.objects.get(uuid=kwargs['uuid'])

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip_archive:
            add_proposal_to_zip(proposal, zip_archive, request)

        filename = f'{proposal.file_name()}.zip'

        response = HttpResponse(buffer.getvalue())
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
