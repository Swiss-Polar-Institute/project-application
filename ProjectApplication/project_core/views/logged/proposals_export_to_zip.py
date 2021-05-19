import io
import zipfile

from django.http import HttpResponse
from django.views import View

from project_core.models import Call
from project_core.views.common.proposal_zip import add_proposal_to_zip


class ProposalsExportZip(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        call = Call.objects.get(id=kwargs['call'])

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip_archive:
            for proposal in call.proposal_set.all():
                add_proposal_to_zip(proposal, zip_archive, request)

        filename = f'{call.short_name}-all_proposals.zip'

        response = HttpResponse(buffer.getvalue())
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
