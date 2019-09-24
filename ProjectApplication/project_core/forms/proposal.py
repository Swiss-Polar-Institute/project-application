from django import forms
from django.forms import ModelForm, Form
from ..models import Person, Proposal, Call, ProposalQAText, CallQuestion
from django.forms.models import inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisations', 'group', ]


class ProposalForm(ModelForm):
    keywords_str = forms.CharField(label='Keywords', help_text='Separated by commas', )
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        call_id = kwargs.pop('call_id', None)
        proposal_id = kwargs.pop('proposal_id', None)

        super(ProposalForm, self).__init__(*args, **kwargs)

        self.fields['call_id'].initial = call_id

        keywords_list = []
        if proposal_id is not None:
            for keyword in Proposal.objects.get(id=proposal_id).keywords.all():
                keywords_list.append(keyword.name)

            self.fields['keywords_str'] = forms.CharField(label='Keywords',
                                                          help_text='Separated by commas',
                                                          initial=', '.join(keywords_list))


        # for question in Call.objects.get(id=call_id).callquestion_set.all():
        #     self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text, widget=forms.Textarea())

    class Meta:
        model = Proposal
        fields = ['title', 'geographical_areas', 'start_timeframe', 'duration']


class QuestionsForProposal(Form):
    def __init__(self, *args, **kwargs):
        self.call_id = kwargs.pop('call_id', None)
        self.proposal_id = kwargs.pop('proposal_id', None)

        assert (self.call_id is not None) or (self.proposal_id is not None)

        super(QuestionsForProposal, self).__init__(*args, **kwargs)

        if self.call_id is not None:
            # This is a form with questions but not answers yet
            for question in Call.objects.get(id=self.call_id).callquestion_set.all():
                self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text,
                                                                                 widget=forms.Textarea())

        if self.proposal_id is not None:
            # This is a form with already answers
            for question in Proposal.objects.get(id=self.proposal_id).call.callquestion_set.all():
                try:
                    answer = ProposalQAText.objects.get(proposal=self.proposal_id, call_question=question.id).answer
                except ObjectDoesNotExist:
                    answer = None

                self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text,
                                                                                 widget=forms.Textarea(),
                                                                                 initial=answer)

    def clean(self):
        cleaned_data = super(QuestionsForProposal, self).clean()

        # list because otherwise dictionary size changes during execution
        # (need to check why exactly)
        for question_number in list(cleaned_data.keys()):
            answer = cleaned_data[question_number]
            question_id = question_number[len('question_'):]

            call_question = CallQuestion.objects.get(id=question_id)

            max_word_length = call_question.answer_max_length
            current_words = len(answer.split())

            if current_words > max_word_length:
                self.add_error(question_number, 'Too long. Current: {} words, maximum: {}'.format(current_words, max_word_length))

        return cleaned_data
    #
    #
    #
    # def clean_question_1(self):
    #     answer = self.cleaned_data['question_1']
    #
    #     words_count = len(answer.split())
    #
    #     if words_count > 5:
    #         raise forms.ValidationError('Too many words1')
    #
    #     return answer
    #
    # def clean_question_2(self):
    #     answer = self.cleaned_data['question_2']
    #
    #     words_count = len(answer.split())
    #
    #     if words_count > 5:
    #         raise forms.ValidationError('Too many words2')
    #
    #     return answer
    #
