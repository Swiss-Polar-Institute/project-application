import botocore
from botocore.exceptions import EndpointConnectionError
from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Form

from project_core.models import ProposalQAFile, ProposalQAText, CallQuestion


class Questions(Form):
    def __init__(self, *args, **kwargs):
        self._call = kwargs.pop('call', None)
        self._proposal = kwargs.pop('proposal', None)

        assert self._call or self._proposal

        super().__init__(*args, **kwargs)

        if self._proposal:
            self._call = self._proposal.call

        for question in self._call.callquestion_set.filter(answer_type=CallQuestion.TEXT).order_by('order'):
            answer = None
            if self._proposal:
                try:
                    answer = ProposalQAText.objects.get(proposal=self._proposal, call_question=question).answer
                except ObjectDoesNotExist:
                    pass

            question_text = question.question_text
            if question.answer_max_length:
                question_text += ' (maximum {} words)'.format(question.answer_max_length)

            self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question_text,
                                                                             widget=forms.Textarea(),
                                                                             initial=answer,
                                                                             help_text=question.question_description)

        for question in self._call.callquestion_set.filter(answer_type=CallQuestion.FILE).order_by('order'):
            try:
                file = ProposalQAFile.objects.get(proposal=self._proposal, call_question=question).file
                self.fields['question_{}'.format(question.pk)] = forms.FileField(label=question.question_text,
                                                                                 help_text=question.question_description,
                                                                                 initial=file)

            except ObjectDoesNotExist:
                question_label = 'question_{}'.format(question.pk)

                question_label_with_prefix = kwargs['prefix'] + '-' + question_label

                if question_label_with_prefix in self.files:
                    self.fields[question_label] = forms.FileField(label=question.question_text,
                                                                  help_text=question.question_description,
                                                                  initial=self.files[question_label_with_prefix])
                else:
                    self.fields[question_label] = forms.FileField(label=question.question_text,
                                                                  help_text=question.question_description)

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    def save_answers(self, proposal):
        all_good = True

        for question, answer in self.cleaned_data.items():
            call_question = CallQuestion.objects.get(id=int(question[len('question_'):]))

            if call_question.answer_type == CallQuestion.TEXT:
                ProposalQAText.objects.update_or_create(
                    proposal=proposal, call_question=call_question,
                    defaults={'answer': answer}
                )
            elif call_question.answer_type == CallQuestion.FILE:
                try:
                    ProposalQAFile.objects.update_or_create(
                        proposal=proposal, call_question=call_question,
                        defaults={'file': answer})
                except EndpointConnectionError:
                    all_good = False
                except botocore.exceptions.ClientError:
                    all_good = False

        return all_good

    def clean(self):
        cleaned_data = super().clean()

        # list because otherwise dictionary size changes during execution
        # (need to check why exactly)
        for question_number in list(cleaned_data.keys()):
            question_id = question_number[len('question_'):]

            call_question = CallQuestion.objects.get(id=question_id)

            if call_question.answer_type == CallQuestion.TEXT:
                answer = cleaned_data[question_number]

                max_word_length = call_question.answer_max_length
                current_words = len(answer.split())

                if max_word_length is not None and current_words > max_word_length:
                    self.add_error(question_number,
                                   'Too long. Current: {} words, maximum: {} words'.format(current_words,
                                                                                           max_word_length))

        return cleaned_data
