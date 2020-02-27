import io
import textwrap

import xlsxwriter
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View

from evaluation.models import Reviewer
from project_core.models import Proposal, Call
from project_core.views.logged.proposal import create_file_name


class ProposalsExportExcel(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._workbook = self._worksheet = None

        # Set by write_call
        self._column_criterion_1 = None
        self._proposal_last_column = None

    def _prepare_styles(self):
        basic_data_properties = {'text_wrap': True, 'border': 1}
        basic_header_properties = {'text_wrap': True, 'bold': True, 'border': 1, 'align': 'center', 'valign': 'bottom'}

        centered_properties = {'align': 'center'}
        centered_text_wrap_properties = dict(**centered_properties, text_wrap=True)
        centered_border_left_properties = dict(**centered_properties, left=1)
        centered_border_right_properties = dict(**centered_properties, right=1)
        centered_border_bottom_properties = dict(**centered_properties, bottom=1)
        centered_border_top_properties = dict(**centered_properties, top=1)
        centered_border_top_left_properties = dict(**centered_properties, top=1, left=1)
        centered_border_top_left_bold_properties = dict(**centered_border_top_left_properties, bold=True)
        centered_border_top_right_properties = dict(**centered_properties, top=1, right=1)
        centered_border_bottom_right_properties = dict(**centered_properties, bottom=1, right=1)
        centered_border_bottom_left_properties = dict(**centered_properties, bottom=1, left=1)

        small_italics_properties = {'font_size': 10, 'italic': True}
        bold_properties = {'bold': True}

        bold_border_left_properties = dict(**bold_properties, left=1)

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

        self._centered = self._workbook.add_format(centered_properties)
        self._centered_text_wrap = self._workbook.add_format(centered_text_wrap_properties)
        self._centered_border_left = self._workbook.add_format(centered_border_left_properties)
        self._centered_border_right = self._workbook.add_format(centered_border_right_properties)
        self._centered_border_bottom = self._workbook.add_format(centered_border_bottom_properties)
        self._centered_border_top = self._workbook.add_format(centered_border_top_properties)
        self._centered_border_top_left = self._workbook.add_format(centered_border_top_left_properties)
        self._centered_border_top_left_bold = self._workbook.add_format(centered_border_top_left_bold_properties)
        self._centered_border_top_right = self._workbook.add_format(centered_border_top_right_properties)
        self._centered_border_bottom_right = self._workbook.add_format(centered_border_bottom_right_properties)
        self._centered_border_bottom_left = self._workbook.add_format(centered_border_bottom_left_properties)

        self._bold_border_left = self._workbook.add_format(bold_border_left_properties)

        self._bold = self._workbook.add_format(bold_properties)
        self._small_italics = self._workbook.add_format(small_italics_properties)

    def _write_call(self, proposal, row, total_number_criteria):
        self._worksheet.set_row(row, 50)
        self._worksheet.set_row(row + 1, 100)
        column = 0
        url = self.request.build_absolute_uri(reverse('logged-proposal-detail', kwargs={'uuid': proposal.uuid}))
        self._worksheet.write(row, column, 'Proposal Number', self._white_header_format)
        self._worksheet.write_url(row + 1, column, url, string=str(proposal.id))
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
            [organisation.name for organisation in proposal.applicant.organisations_ordered_by_name()]),
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
        self._worksheet.merge_range(row + 2, 0, row + 2, 7, feedback_question_text, self._feedback_question_format)
        self._worksheet.set_row(row + 2, 50)

        self._worksheet.merge_range(row + 3, 0, row + 3, 7, 'Fill in here', self._feedback_answer_format)
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

        self._proposal_last_column = column

    def _write_marking_scale_box(self, initial_row, initial_column):
        scale = [('OUTSTANDING', '9-10'),
                 ('VERY GOOD', '7-8'),
                 ('GOOD', '6-5'),
                 ('AVERAGE', '4-3'),
                 ('POOR', '2-1'),
                 ('NOT RELEVANT', '0')
                 ]

        self._worksheet.write(initial_row, initial_column, 'MARKING SCALE', self._centered_border_top_left_bold)
        self._worksheet.write(initial_row, initial_column + 1, '', self._centered_border_top_right)

        last_row = initial_row
        for index, rate in enumerate(scale):
            self._worksheet.write(initial_row + index + 1, initial_column, rate[0], self._centered_border_left)
            self._worksheet.write(initial_row + index + 1, initial_column + 1, rate[1], self._centered_border_right)

            last_row += 1

        self._worksheet.write(last_row, initial_column, '', self._centered_border_top)
        self._worksheet.write(last_row, initial_column + 1, '', self._centered_border_top)

    def _write_evaluation_criteria(self, initial_row, initial_column, border_right_column):
        evaluation_criteria = [('1', 'SCIENTIFIC MERIT OF THE PROJECT',
                                'What is the scientific merit of the proposed project? Does the project contribute to relevant scientific questions?'),
                               ('2', 'ORIGINALITY OF THE PROJECT',
                                'Novelty and originality of the approach and proposed activities'),
                               ('3', 'FEASIBILITY OF THE PROJECT',
                                'Is the proposed scientific methodology feasible under the given environmental, financial and logistic context? What are the risks and how important are they? Is the proposed timeframe and budget realistic?'),
                               ('4', 'EXPERIENCE AND EXPERTISE OF THE PI AND PARTNERS',
                                'What is the applicant’s track record so far (academic excellence)?; What is the potential for the applicant to benefit from this field trip?; Is the applicant’s environment (institute/lab) and support appropriate for the success of the proposed activity?'),
                               ('5', 'IMPACT OF THE REQUESTED FUNDING',
                                'How important is the additional funding provided by the SPI Exploratory Grant for the successful undertaking of the proposed project? What does the additional funding enable to do and to which extend is this instrumental for the project? Does it add value to the project?')
                               ]

        self._worksheet.write(initial_row, initial_column, 'EVALUATION CRITERIA', self._bold_border_left)

        last_row = initial_row

        self._worksheet.write(initial_row, border_right_column, '', self._centered_border_right)

        for index, row in enumerate(evaluation_criteria):
            self._worksheet.write(initial_row + index + 1, initial_column, row[0], self._centered_border_left)
            self._worksheet.write(initial_row + index + 1, initial_column + 1, row[1], self._centered_text_wrap)

            if len(row[1]) > 35:
                # This is going to be (likely) a multi-line row. Default height=15 from xlsxwriter
                self._worksheet.set_row(initial_row + index + 1, 30)

            self._worksheet.write(initial_row + index + 1, initial_column + 2, row[2], self._small_italics)
            self._worksheet.write(initial_row + index + 1, border_right_column, '', self._centered_border_right)

            last_row += 1

        for column in range(initial_column, border_right_column + 1):
            self._worksheet.write(initial_row - 1, column, '', self._centered_border_bottom)
            self._worksheet.write(last_row + 1, column, '', self._centered_border_top)

    def get(self, request, *args, **kwargs):
        call_id = kwargs['call']

        # Proposals get filter later based on call_id being None (all of them) or not
        proposals = Proposal.objects.all().order_by('title')
        proposals = Reviewer.filter_proposals(proposals, self.request.user)

        date = timezone.now().strftime('%Y%m%d-%H%M%S')
        call = None
        if call_id:
            call = Call.objects.get(id=call_id)
            filename = create_file_name('proposals-{}-{}.xlsx', call_id)
            proposals = proposals.filter(call=call)
        else:
            filename = 'proposals-all-{}.xlsx'.format(date)

        output = io.BytesIO()
        self._workbook = xlsxwriter.Workbook(output)
        self._worksheet = self._workbook.add_worksheet()

        self._prepare_styles()

        # Writes main information
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

        # Criterion headers
        criterion_header_texts = ['SCIENTIFIC MERIT OF THE PROJECT', 'ORIGINALITY OF THE PROJECT',
                                  'FEASIBILITY OF THE PROJECT', 'EXPERIENCE AND EXPERTISE OF THE APPLICANT',
                                  'IMPACT OF THE REQUESTED FUNDING']

        # Writes the information for each proposal
        for index, proposal in enumerate(proposals):
            self._write_call(proposal, row_initial_proposal + (index * 7), len(criterion_header_texts))
            # self.worksheet.write(num + 2, 0, proposal.title)

        # Adds headers of the criterion
        criterion_last_column = None
        for index, criterion_header_text in enumerate(criterion_header_texts):
            column = self._column_criterion_1 + index * 2
            self._worksheet.merge_range(row_initial_proposal - 1, column, row_initial_proposal - 1,
                                        column + 1, criterion_header_text,
                                        self._yellow_cell_format)

            criterion_last_column = column + 1

        self._worksheet.write(row_initial_proposal - 1, criterion_last_column + 1, 'TOTAL', self._yellow_cell_format)

        self._write_marking_scale_box(1, 5)

        self._write_evaluation_criteria(1, 8, self._proposal_last_column)

        self._worksheet.freeze_panes(10, 6)

        self._workbook.close()

        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
