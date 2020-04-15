import codecs
import csv

from django.http import HttpResponse
from django.views import View

from evaluation.models import Reviewer
from project_core.models import Proposal
from project_core.views.logged.proposal import create_file_name


class ProposalsExportCsvSummary(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        call_id = kwargs.get('call', None)
        response = HttpResponse(content_type='text/csv')

        filename = create_file_name('proposal-summary-{}-{}.csv', call_id)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)

        headers = ['Academic Title', 'First Name', 'Surname', 'Institutions', 'Proposal Title', 'Keywords',
                   'Requested Amount (CHF)', 'Geographic Focus']

        proposals = Proposal.objects.all()

        if call_id is not None:
            # We are filtering by a specific Call: we are exporting proposals for only call_id
            proposals.filter(call_id=call_id)
        else:
            # We are adding the Call Name: we are exporting proposals for all the calls
            headers = ['Call Name'] + headers

        proposals = Reviewer.filter_proposals(proposals, self.request.user)

        writer.writerow(headers)

        for proposal in proposals.order_by('id'):
            academic_title = proposal.applicant.academic_title
            first_name = proposal.applicant.person.first_name
            surname = proposal.applicant.person.surname

            institutions = proposal.applicant.organisations_ordered_by_name_str()
            title = proposal.title

            keywords = proposal.keywords_enumeration()
            requested_amount = proposal.total_budget()
            geographic_focus = proposal.geographical_areas_enumeration()

            row = [academic_title, first_name, surname, institutions, title, keywords, requested_amount,
                   geographic_focus]

            if call_id is None:
                # We are adding the Call name: we are exporting proposals for different calls
                row = [proposal.call.long_name] + row

            writer.writerow(row)

        return response