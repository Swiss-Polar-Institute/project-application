import io
import textwrap

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
        basic_data_properties = {'text_wrap': True, 'border': 1}
        basic_header_properties = {'text_wrap': True, 'bold': True, 'border': 1, 'align': 'center', 'valign': 'bottom'}

        white_header_properties = dict(**basic_header_properties, top=2)
        grey_header_properties = dict(**basic_header_properties, bg_color='#d6dce5', top=2)
        green_header_properties = dict(**basic_header_properties, bg_color='#a9d18e', top=2)
        yellow_header_properties = dict(**basic_header_properties, bg_color='#fff2cc', top=2)
        blue_header_properties = dict(**basic_header_properties, bg_color='#dae3f3', top=2)
        orange_header_properties = dict(**basic_header_properties, bg_color='#f4b183', top=2)
        feedback_question_properties = dict(**basic_data_properties, bg_color='#d0cece', right=2)
        feedback_answer_properties = dict(**basic_data_properties, bg_color='#d0cece', bottom=2, right=2, italic=True)

        white_header_format = self._workbook.add_format(white_header_properties)
        grey_header_format = self._workbook.add_format(grey_header_properties)
        green_header_format = self._workbook.add_format(green_header_properties)
        yellow_header_format = self._workbook.add_format(yellow_header_properties)
        blue_header_format = self._workbook.add_format(blue_header_properties)
        orange_header_format = self._workbook.add_format(orange_header_properties)
        feedback_question_format = self._workbook.add_format(feedback_question_properties)
        feedback_answer_format = self._workbook.add_format(feedback_answer_properties)

        data_format = self._workbook.add_format(basic_data_properties)

        self._worksheet.set_row(row, 50)
        self._worksheet.set_row(row + 1, 100)

        column = 0
        self._worksheet.write(row, column, 'Proposal Number', white_header_format)
        self._worksheet.write(row + 1, column, proposal.id, data_format)
        self._worksheet.set_column(column, column, 15)

        column = 1
        self._worksheet.write(row, column, 'Applicant title', grey_header_format)
        self._worksheet.write(row + 1, column, proposal.applicant.academic_title.title, data_format)
        self._worksheet.set_column(column, column, 10)

        column = 2
        self._worksheet.write(row, column, 'Applicant name', grey_header_format)
        self._worksheet.write(row + 1, column, proposal.applicant.person.full_name(), data_format)
        self._worksheet.set_column(column, column, 20)

        column = 3
        self._worksheet.write(row, column, 'Institution', grey_header_format)
        self._worksheet.write(row + 1, column, ', '.join(
            [organisation.short_name for organisation in proposal.applicant.organisations_ordered_by_name()]),
                              data_format)
        self._worksheet.set_column(column, column, 15)

        column = 4
        self._worksheet.write(row, column, 'Title of the project', green_header_format)
        self._worksheet.write(row + 1, column, proposal.title, data_format)
        self._worksheet.set_column(column, column, 25)

        column = 5
        self._worksheet.write(row, column, 'Geographic focus', green_header_format)
        self._worksheet.write(row + 1, column,
                              ', '.join([area.name for area in proposal.geographical_areas.all().order_by('name')]),
                              data_format)
        self._worksheet.set_column(column, column, 25)

        column = 6
        self._worksheet.write(row, column, 'Keywords', green_header_format)
        self._worksheet.write(row + 1, column, proposal.keywords_enumeration(), data_format)
        self._worksheet.set_column(column, column, 30)

        column = 7
        self._worksheet.write(row, column, 'Budget requested', white_header_format)
        self._worksheet.write(row + 1, column, proposal.total_budget(), data_format)
        self._worksheet.set_column(column, column, 10)

        feedback_question_text = textwrap.dedent('''\
        FEEDBACK TO APPLICANTS: What are the strengths and weaknesses of the proposal? Please write
        3-5 lines of text that the Swiss Polar Institute can send to applicants in case their proposal is not funded.
        Be careful to avoid any formulation which could cause misunderstandings or seem offensive.''')
        self._worksheet.merge_range(f'A{row + 3}:H{row + 3}', feedback_question_text, feedback_question_format)
        self._worksheet.set_row(row + 2, 50)

        self._worksheet.merge_range(f'A{row + 4}:H{row + 4}', 'Fill in here', feedback_answer_format)
        self._worksheet.set_row(row + 3, 50)

        # Answers from the committee
        column = 8
        total_number_criteria = 5
        score_column_width = 12
        for criterion_n in range(1, total_number_criteria):
            self._worksheet.write(row, column, f'Criterion {criterion_n}: score', yellow_header_format)
            self._worksheet.write(row + 1, column, '', data_format)
            self._worksheet.set_column(column, column, score_column_width)

            self._worksheet.write(row, column + 1, f'Criterion {criterion_n}: remarks', yellow_header_format)
            self._worksheet.write(row + 1, column + 1, '', data_format)
            self._worksheet.set_column(column + 1, column + 1, 35)

            column += 2

        self._worksheet.write(row, column, f'Total score criteria 1-{total_number_criteria}', yellow_header_format)
        self._worksheet.write(row+1, column, '', data_format)
        self._worksheet.set_column(column, column, score_column_width)

        column += 1
        self._worksheet.write(row, column, 'Budget proposed by reviewer', blue_header_format)
        self._worksheet.write(row+1, column, '', data_format)
        self._worksheet.set_column(column, column, score_column_width)

        column += 1
        self._worksheet.write(row, column, 'Budget remarks', blue_header_format)
        self._worksheet.write(row+1, column, '', data_format)
        self._worksheet.set_column(column, column, 30)

        column += 1
        self._worksheet.write(row, column, 'Optional additional remarks to the panel', orange_header_format)
        self._worksheet.write(row+1, column, '', data_format)
        self._worksheet.set_column(column, column, 50)

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

        self._worksheet.set_row(0, 20)

        self._worksheet.write(2, 0, 'To be returned to spi-grants@epfl.ch')
        italic_format = self._workbook.add_format({'italic': True})
        self._worksheet.write_rich_string(4, 0, 'Name of the reviewer: ', italic_format, 'please fill in')

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
