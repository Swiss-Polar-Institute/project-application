from django import forms
from django.forms import ModelForm, Form
from ..models import Person, Proposal, Call
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
    def __init__(self, call_id, *args, **kwargs):
        self.call_id = call_id

        super(QuestionsForProposal, self).__init__(*args, **kwargs)

        for question in Call.objects.get(id=call_id).callquestion_set.all():
            self.fields['question_{}'.format(question.pk)] = forms.CharField(label=question.question_text, widget=forms.Textarea())