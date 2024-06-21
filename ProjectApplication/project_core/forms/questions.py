import logging

import botocore
from botocore.exceptions import EndpointConnectionError
from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Form

from project_core.models import ProposalQAFile, ProposalQAText, CallQuestion, CallPart
from project_core.utils.utils import external_file_validator
from ckeditor_uploader.widgets import CKEditorUploadingWidget

logger = logging.getLogger('project_core')


class Questions(Form):
    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._proposal = kwargs.pop('proposal', None)
        self._call_part: CallPart = kwargs.pop('call_part')
        only_files = kwargs.pop('only_files', False)

        assert self._call or self._proposal

        super().__init__(*args, **kwargs)

        self._questions_answers_text = []
        self._questions_answers_file = []

        if self._proposal:
            self._call = self._proposal.call

        if only_files is False:
            for question in self._call_part.questions_type_text():
                answer = None
                if self._proposal:
                    try:
                        answer = ProposalQAText.objects.get(proposal=self._proposal, call_question=question).answer
                    except ObjectDoesNotExist:
                        pass

                question_text = question.question_text
                if question.answer_max_length:
                    question_text += ' (maximum {} words)'.format(question.answer_max_length)

                self.fields['question_{}'.format(question.pk)] = forms.CharField(
                    label=question_text,
                    widget=CKEditorUploadingWidget(),
                    initial=answer,
                    help_text=question.question_description,
                    required=False  # Set required to False here
                )

                self._questions_answers_text.append({'question': question, 'answer': answer})

        for question in self._call_part.questions_type_files():
            question_label = 'question_{}'.format(question.pk)

            try:
                file = ProposalQAFile.objects.get(proposal=self._proposal, call_question=question).file
                self.fields[question_label] = forms.FileField(
                    label=question.question_text,
                    help_text=question.question_description,
                    initial=file,
                    required=False  # Set required to False here
                )
            except ObjectDoesNotExist:
                question_label_with_prefix = kwargs['prefix'] + '-' + question_label

                if question_label_with_prefix in self.files:
                    self.fields[question_label] = forms.FileField(
                        label=question.question_text,
                        help_text=question.question_description,
                        initial=self.files[question_label_with_prefix],
                        required=False  # Set required to False here
                    )
                else:
                    self.fields[question_label] = forms.FileField(
                        label=question.question_text,
                        help_text=question.question_description,
                        required=False  # Set required to False here
                    )

            self._questions_answers_file.append({'question': question, 'answer': self.fields[question_label].initial})

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        # Set required to False for all fields
        for field in self.fields.values():
            field.required = False

    def questions_answers_text(self):
        return self._questions_answers_text

    def questions_answers_file(self):
        return self._questions_answers_file

    def save_answers(self, proposal):
        all_good = True

        if not self.is_bound:
            logger.warning(f"Form is not bound")
            return False

        self.full_clean()  # Ensure the form is cleaned to populate cleaned_data

        for question in self.fields:
            answer = self.cleaned_data.get(question)
            call_question = CallQuestion.objects.get(id=int(question[len('question_'):]))

            if call_question.answer_type == CallQuestion.TEXT:
                ProposalQAText.objects.update_or_create(
                    proposal=proposal, call_question=call_question,
                    defaults={'answer': answer}
                )
            elif call_question.answer_type == CallQuestion.FILE:
                if not answer:
                    file_to_delete = None
                    try:
                        file_to_delete = ProposalQAFile.objects.get(proposal=proposal, call_question=call_question)
                    except ObjectDoesNotExist:
                        pass

                    if file_to_delete:
                        file_to_delete.delete()
                else:
                    if '/' not in answer.name:
                        answer.name = f'{self._call.id}-{proposal.id}-{answer.name}'
                    try:
                        ProposalQAFile.objects.update_or_create(
                            proposal=proposal, call_question=call_question,
                            defaults={'file': answer}
                        )
                    except EndpointConnectionError:
                        all_good = False
                        logger.warning(
                            f'NOTIFY: Saving file for question failed (proposal: {proposal.id} call_question: {call_question.id}) -EndpointConnectionError')
                    except botocore.exceptions.ClientError:
                        all_good = False
                        logger.warning(
                            f'NOTIFY: Saving file for question failed (proposal: {proposal.id} call_question: {call_question.id}) -ClientError')

        return all_good

    def clean(self):
        cleaned_data = super().clean()

        for question_number in list(cleaned_data.keys()):
            question_id = question_number[len('question_'):]

            call_question = CallQuestion.objects.get(id=question_id)

            if call_question.answer_type == CallQuestion.TEXT:
                answer = cleaned_data[question_number]

                max_word_length = call_question.answer_max_length
                current_words = len(answer.split())

                if max_word_length is not None and current_words > max_word_length:
                    self.add_error(
                        question_number,
                        'Too long. Current: {} words, maximum: {} words'.format(current_words, max_word_length)
                    )

        return cleaned_data

