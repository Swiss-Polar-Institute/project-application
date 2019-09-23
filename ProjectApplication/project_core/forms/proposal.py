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

    class Meta:
        model = Proposal
        fields = ['title', 'geographical_area']

    def save(self, commit=True):
        # TODO: check what happens with keyword_str
        return super(ProposalForm, self).save(commit=commit)

