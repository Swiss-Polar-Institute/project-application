from django import forms
from django.forms import ModelForm
from ..models import Person, Proposal
from django.forms.models import inlineformset_factory


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['academic_title', 'first_name', 'surname', 'organisation', 'group', ]


class ProposalForm(ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'geographical_area']

