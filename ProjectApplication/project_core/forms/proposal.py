from django import forms
from django.forms import ModelForm, Form
from ..models import Person, Proposal, Call, ProposalQAText
from django.forms.models import inlineformset_factory


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisations', 'group', ]


class ProposalForm(ModelForm):
    keywords_str = forms.CharField(label='Keywords', help_text='Separated by commas', )
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        call_id = kwargs.pop('call_id', None)
        super(ProposalForm, self).__init__(*args, **kwargs)

        self.fields['call_id'].initial = call_id

        # for question in Call.objects.get(id=call_id).callquestion_set.all():
        #     self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text, widget=forms.Textarea())

    class Meta:
        model = Proposal
        fields = ['title', 'geographical_areas', 'start_timeframe', 'duration']


class QuestionsForProposal(Form):
    def __init__(self, *args, **kwargs):
        call_id = kwargs.pop('call_id', None)
        proposal_id = kwargs.pop('proposal_id', None)

        assert (call_id is not None) or (proposal_id is not None)

        super(QuestionsForProposal, self).__init__(*args, **kwargs)

        if call_id is not None:
            # This is a form with questions but not answers yet
            for question in Call.objects.get(id=call_id).callquestion_set.all():
                self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text,
                                                                                 widget=forms.Textarea())

        if proposal_id is not None:
            # This is a form with already answers
            for question in Proposal.objects.get(id=proposal_id).call.callquestion_set.all():
                answer = ProposalQAText.objects.get(proposal=proposal_id, call_question=question.id).answer

                self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text,
                                                                                 widget=forms.Textarea(),
                                                                                 initial=answer)