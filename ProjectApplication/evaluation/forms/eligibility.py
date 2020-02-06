from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse

from project_core.models import Proposal


class EligibilityDecisionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._proposal_uuid = kwargs.pop('proposal_uuid')
        super().__init__(*args, **kwargs)

        YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]
        self.fields['eligible'] = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
        self.fields['comment'] = forms.CharField(label='Comment<span class="asteriskField">*</span>', required=False, max_length=1000,
                                                 help_text='Maximum length 1000 characters',
                                                 widget=forms.Textarea(attrs={'rows': 4}))

        proposal = Proposal.objects.get(uuid=self._proposal_uuid)

        if proposal.eligibility == Proposal.ELIGIBLE:
            self.fields['eligible'].initial = True
        elif proposal.eligibility == Proposal.NOTELIGIBLE:
            self.fields['eligible'].initial = False

        self.fields['comment'].initial = proposal.eligibility_comment

        self.helper = FormHelper(self)
        self.helper.form_action = reverse('logged-proposal-eligibility-update', kwargs={'uuid': self._proposal_uuid})
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.layout = Layout(
            Div(
                Div('eligible')
            ),
            Div(
                Div('comment')
            )
        )

    def clean(self):
        super().clean()

        if 'eligible' in self.cleaned_data and 'comment' in self.cleaned_data:
            if self.cleaned_data['eligible'] is False and not self.cleaned_data['comment']:
                raise forms.ValidationError({'comment': 'Comment is mandatory if the proposal is not eligible'})

    def save_eligibility(self):
        eligible = self.cleaned_data['eligible']
        comment = self.cleaned_data.get('comment', None)

        proposal = Proposal.objects.get(uuid=self._proposal_uuid)

        if eligible == 'True':
            proposal.eligibility = Proposal.ELIGIBLE
        else:
            proposal.eligibility = Proposal.NOTELIGIBLE

        proposal.eligibility_comment = comment

        proposal.save()