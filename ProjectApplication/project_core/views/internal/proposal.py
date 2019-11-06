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

        # Set by write_call
        self._column_criterion_1 = None

    def _prepare_styles(self):
        basic_data_properties = {'text_wrap': True, 'border': 1}
        basic_header_properties = {'text_wrap': True, 'bold': True, 'border': 1, 'align': 'center', 'valign': 'bottom'}

        white_header_properties = dict(**basic_header_properties, top=2)
        grey_header_properties = dict(**basic_header_properties, bg_color='#d6dce5', top=2)
        green_header_properties = dict(**basic_header_properties, bg_color='#a9d18e', top=2)
        yellow_cell_properties = dict(**basic_header_properties, bg_color='#fff2cc')
        yellow_header_properties = dict(**yellow_cell_properties, top=2)
        blue_header_properties = dict(**basic_header_properties, bg_color='#dae3f3', top=2)
        orange_header_properties = dict(**basic_header_properties, bg_color='#f4b183', top=2)
        feedback_question_properties = dict(**basic_data_properties, bg_color='#d0cece', right=2)
        feedback_answer_properties = dict(**basic_data_properties, bg_color='#d0cece', bottom=2, right=2, italic=True)

        self._white_header_format = self._workbook.add_format(white_header_properties)
        self._grey_header_format = self._workbook.add_format(grey_header_properties)
        self._green_header_format = self._workbook.add_format(green_header_properties)
        self._yellow_cell_format = self._workbook.add_format(yellow_cell_properties)
        self._yellow_header_format = self._workbook.add_format(yellow_header_properties)
        self._blue_header_format = self._workbook.add_format(blue_header_properties)
        self._orange_header_format = self._workbook.add_format(orange_header_properties)
        self._feedback_question_format = self._workbook.add_format(feedback_question_properties)
        self._feedback_answer_format = self._workbook.add_format(feedback_answer_properties)
        self._data_format = self._workbook.add_format(basic_data_properties)

    def _write_call(self, proposal, row, total_number_criteria):
        self._worksheet.set_row(row, 50)
        self._worksheet.set_row(row + 1, 100)

        column = 0
        self._worksheet.write(row, column, 'Proposal Number', self._white_header_format)
        self._worksheet.write(row + 1, column, proposal.id, self._data_format)
        self._worksheet.set_column(column, column, 15)

        column = 1
        self._worksheet.write(row, column, 'Applicant title', self._grey_header_format)
        self._worksheet.write(row + 1, column, proposal.applicant.academic_title.title, self._data_format)
        self._worksheet.set_column(column, column, 10)

        column = 2
        self._worksheet.write(row, column, 'Applicant name', self._grey_header_format)
        self._worksheet.write(row + 1, column, proposal.applicant.person.full_name(), self._data_format)
        self._worksheet.set_column(column, column, 20)

        column = 3
        self._worksheet.write(row, column, 'Institution', self._grey_header_format)
        self._worksheet.write(row + 1, column, ', '.join(
            [organisation.short_name for organisation in proposal.applicant.organisations_ordered_by_name()]),
                              self._data_format)
        self._worksheet.set_column(column, column, 15)

        column = 4
        self._worksheet.write(row, column, 'Title of the project', self._green_header_format)
        self._worksheet.write(row + 1, column, proposal.title, self._data_format)
        self._worksheet.set_column(column, column, 25)

        column = 5
        self._worksheet.write(row, column, 'Geographic focus', self._green_header_format)
        self._worksheet.write(row + 1, column,
                              ', '.join([area.name for area in proposal.geographical_areas.all().order_by('name')]),
                              self._data_format)
        self._worksheet.set_column(column, column, 25)

        column = 6
        self._worksheet.write(row, column, 'Keywords', self._green_header_format)
        self._worksheet.write(row + 1, column, proposal.keywords_enumeration(), self._data_format)
        self._worksheet.set_column(column, column, 30)

        column = 7
        self._worksheet.write(row, column, 'Budget requested', self._white_header_format)
        self._worksheet.write(row + 1, column, proposal.total_budget(), self._data_format)
        self._worksheet.set_column(column, column, 10)

        feedback_question_text = textwrap.dedent('''\
        FEEDBACK TO APPLICANTS: What are the strengths and weaknesses of the proposal? Please write
        3-5 lines of text that the Swiss Polar Institute can send to applicants in case their proposal is not funded.
        Be careful to avoid any formulation which could cause misunderstandings or seem offensive.''')
        self._worksheet.merge_range(f'A{row + 3}:H{row + 3}', feedback_question_text, self._feedback_question_format)
        self._worksheet.set_row(row + 2, 50)

        self._worksheet.merge_range(f'A{row + 4}:H{row + 4}', 'Fill in here', self._feedback_answer_format)
        self._worksheet.set_row(row + 3, 50)

        # Answers from the committee
        column = 8
        score_column_width = 12

        self._column_criterion_1 = column
        for criterion_n in range(1, total_number_criteria + 1):
            self._worksheet.write(row, column, f'Criterion {criterion_n}: score', self._yellow_header_format)
            self._worksheet.write(row + 1, column, '', self._data_format)
            self._worksheet.set_column(column, column, score_column_width)

            self._worksheet.write(row, column + 1, f'Criterion {criterion_n}: remarks', self._yellow_header_format)
            self._worksheet.write(row + 1, column + 1, '', self._data_format)
            self._worksheet.set_column(column + 1, column + 1, 35)

            column += 2

        self._worksheet.write(row, column, f'Total score criteria 1-{total_number_criteria}',
                              self._yellow_header_format)
        self._worksheet.write(row + 1, column, '', self._data_format)
        self._worksheet.set_column(column, column, score_column_width)

        column += 1
        self._worksheet.write(row, column, 'Budget proposed by reviewer', self._blue_header_format)
        self._worksheet.write(row + 1, column, '', self._data_format)
        self._worksheet.set_column(column, column, score_column_width)

        column += 1
        self._worksheet.write(row, column, 'Budget remarks', self._blue_header_format)
        self._worksheet.write(row + 1, column, '', self._data_format)
        self._worksheet.set_column(column, column, 30)

        column += 1
        self._worksheet.write(row, column, 'Optional additional remarks to the panel', self._orange_header_format)
        self._worksheet.write(row + 1, column, '', self._data_format)
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

        self._prepare_styles()

        cell_format = self._workbook.add_format({'bold': True, 'font_size': 13})
        if call_id:
            self._worksheet.write(0, 0, call.long_name, cell_format)
        else:
            self._worksheet.write(0, 0, 'All calls', cell_format)

        self._worksheet.set_row(0, 20)

        self._worksheet.write(2, 0, 'To be returned to spi-grants@epfl.ch')
        italic_format = self._workbook.add_format({'italic': True})
        self._worksheet.write_rich_string(4, 0, 'Name of the reviewer: ', italic_format, 'please fill in')

        row_initial_proposal = 10

        criterion_header_texts = ['SCIENTIFIC MERIT OF THE PROJECT', 'ORIGINALITY OF THE PROJECT',
                                  'FEASIBILITY OF THE PROJECT', 'EXPERIENCE AND EXPERTISE OF THE APPLICANT',
                                  'IMPACT OF THE REQUESTED FUNDING']

        for index, proposal in enumerate(proposals):
            self._write_call(proposal, row_initial_proposal + (index * 7), len(criterion_header_texts))
            # self.worksheet.write(num + 2, 0, proposal.title)

        criterion_last_column = None
        for index, criterion_header_text in enumerate(criterion_header_texts):
            column = self._column_criterion_1 + index * 2
            self._worksheet.merge_range(row_initial_proposal - 1, column, row_initial_proposal - 1,
                                        column + 1, criterion_header_text,
                                        self._yellow_cell_format)

            criterion_last_column = column + 1

        self._worksheet.write(row_initial_proposal - 1, criterion_last_column+1, 'TOTAL', self._yellow_cell_format)
        self._workbook.close()

        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
