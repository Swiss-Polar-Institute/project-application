import io
import zipfile

from django.http import FileResponse
from django.views import View

from project_core.models import Call
from project_core.views.common.proposal_zip import add_proposal_to_zip


class CreateZipFile:
    def __init__(self, call, request):
        self._proposals = iter(call.proposal_set.all())
        self._request = request

        self._buffer = io.BytesIO()
        self._zipfile = zipfile.ZipFile(self._buffer, 'w')
        self._used_directory_names = []

        self._last_read_position = 0
        self._last_wrote_position = 0

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
        read_buffer = self._buffer.read(size)
        self._last_read_position = self._buffer.tell()

        if len(read_buffer) < size:
            self._add_new_proposal()
            self._buffer.seek(self._last_read_position)
            read_buffer += self._buffer.read(size - len(read_buffer))
            self._last_read_position = self._buffer.tell()

        return read_buffer


class ProposalsExportZip(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        call = Call.objects.get(id=kwargs['call'])

        filename = f'{call.short_name}-all_proposals.zip'
        filename = filename.replace(' ', '_')

        response = FileResponse(CreateZipFile(call, request),
                                filename=filename)

        return response
