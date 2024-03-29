import io
import zipfile

from django.http import FileResponse
from django.utils import timezone
from django.views import View

from evaluation.models import Reviewer
from project_core.models import Call, Proposal
from project_core.views.common.proposal_zip import add_proposal_to_zip


class CreateZipFile:
    def __init__(self, proposals, request):
        self._proposals = iter(proposals)
        self._request = request

        self._buffer = io.BytesIO()
        self._zipfile = zipfile.ZipFile(self._buffer, 'w')

        self._used_directory_names = []

        self._last_read_position = 0

        with self._zipfile.open('README.txt', mode='w') as readme_file:
            readme_file.write(b'This ZIP file includes confidential proposals and personal information. Please keep it private and confidential.')

        self._last_wrote_position = self._buffer.tell()

    def _add_new_proposal(self):
        try:
            proposal = next(self._proposals)
        except StopIteration:
            self._zipfile.close()
            return

        self._buffer.seek(self._last_wrote_position)
        directory_name = add_proposal_to_zip(proposal, self._zipfile,
                                             self._request, self._used_directory_names)
        self._last_wrote_position = self._buffer.tell()

        self._used_directory_names.append(directory_name)

    def read(self, size):
        first_read = self._last_read_position == 0

        self._buffer.seek(self._last_read_position)
        read_buffer = self._buffer.read(size)
        self._last_read_position = self._buffer.tell()

        if len(read_buffer) < size and not first_read:
            self._add_new_proposal()
            self._buffer.seek(self._last_read_position)
            read_buffer += self._buffer.read(size - len(read_buffer))
            self._last_read_position = self._buffer.tell()

        return read_buffer


class ProposalsExportZip(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if 'call' in kwargs:
            call = Call.objects.get(id=kwargs['call'])
            proposals = call.proposal_set.all()

            base_filename = f'proposals-{call.short_name}'
        else:
            proposals = Proposal.objects.all()
            proposals = Reviewer.filter_proposals(proposals, self.request.user)

            base_filename = 'proposals-all'

        date = timezone.now().strftime('%Y%m%d-%H%M%S')
        filename = f'{base_filename}-{date}.zip'
        filename = filename.replace(' ', '_')

        return FileResponse(CreateZipFile(proposals, request),
                            filename=filename)
