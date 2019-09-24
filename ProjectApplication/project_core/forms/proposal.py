from django import forms
from django.forms import ModelForm
from ..models import Person, Proposal
from django.forms.models import inlineformset_factory


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisation', 'group', ]


class ProposalForm(ModelForm):
    keywords_str = forms.CharField(label='Keywords', help_text='Separated by commas', )
    call_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        call_id = kwargs.pop('call_id', None)
        super(ProposalForm, self).__init__(*args, **kwargs)

        self.fields['call_id'].initial = call_id


    class Meta:
        model = Proposal
        fields = ['title', 'geographical_areas']
