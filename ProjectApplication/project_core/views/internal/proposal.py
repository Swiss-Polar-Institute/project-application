import io

import xlsxwriter
from django.http import HttpResponse
from django.utils import timezone
from django.views import View

from project_core.models import Proposal, Call


class ProposalsExportExcel(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._workbook = self._worksheet = None

    def write_call(self, proposal, row):
        format = self._workbook.add_format({'text_wrap': True, 'bold': True})
        format.set_align('center')
        format.set_align('bottom')

        self._worksheet.set_row(row, 50)

        column = 0
        self._worksheet.write(row, column, 'Proposal Number', format)
        self._worksheet.write(row + 1, column, proposal.id)
        self._worksheet.set_column(column, column, 15)

        column = 1
        self._worksheet.write(row, column, 'Applicant title', format)
        self._worksheet.write(row + 1, column, proposal.applicant.academic_title.title)
        self._worksheet.set_column(column, column, 10)

        column = 2
        self._worksheet.write(row, column, 'Applicant name', format)
        self._worksheet.write(row + 1, column, proposal.applicant.person.full_name())
        self._worksheet.set_column(column, column, 20)

        column = 3
        self._worksheet.write(row, column, 'Institution', format)
        self._worksheet.write(row + 1, column, ', '.join([organisation.short_name for organisation in proposal.applicant.organisations_ordered_by_name()]))
        self._worksheet.set_column(column, column, 15)

        column = 4
        self._worksheet.write(row, column, 'Title of the project', format)
        self._worksheet.write(row + 1, column, proposal.title)
        self._worksheet.set_column(column, column, 25)

        column = 5
        self._worksheet.write(row, column, 'Geographic focus', format)
        self._worksheet.write(row + 1, column, ', '.join([area.name for area in proposal.geographical_areas.all().order_by('name')]))
        self._worksheet.set_column(column, column, 25)

        column = 6
        self._worksheet.write(row, column, 'Keywords', format)
        self._worksheet.write(row + 1, column, proposal.keywords_enumeration())
        self._worksheet.set_column(column, column, 30)

        column = 7
        self._worksheet.write(row, column, 'Budget requested', format)
        self._worksheet.write(row + 1, column, proposal.total_budget())
        self._worksheet.set_column(column, column, 10)


    def get(self, request, *args, **kwargs):
        call_id = kwargs.get('call', None)

        proposals = Proposal.objects.all().order_by('title')

        date = timezone.now().strftime('%Y%m%d-%H%M%S')
        call = None
        if call_id:
            call = Call.objects.get(id=call_id)
            proposals = proposals.filter(call_id=call_id)
            filename = 'proposals-{}-{}.xlsx'.format(call.short_name, date)
        else:
            filename = 'proposals-all-{}.xlsx'.format(date)

        output = io.BytesIO()
        self._workbook = xlsxwriter.Workbook(output)
        self._worksheet = self._workbook.add_worksheet()

        cell_format = self._workbook.add_format({'bold': True, 'font_size': 13})
        if call_id:
            self._worksheet.write(0, 0, call.long_name, cell_format)
        else:
            self._worksheet.write(0, 0, 'All calls', cell_format)

        self._worksheet.write(2, 0, 'To be returned to spi-grants@epfl.ch')

        for num, proposal in enumerate(proposals):
            self.write_call(proposal, 10 + (num * 7))
            # self.worksheet.write(num + 2, 0, proposal.title)

        self._workbook.close()

        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
