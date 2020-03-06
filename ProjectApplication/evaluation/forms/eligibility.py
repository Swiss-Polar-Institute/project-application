from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML
from django import forms
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from ProjectApplication import settings
from project_core.forms.utils import cancel_edit_button
from project_core.models import Proposal
from project_core.utils import user_is_in_group_name


class EligibilityDecisionForm(forms.Form):
    FORM_NAME = 'eligibility_decision_form'

    def __init__(self, *args, **kwargs):
        self._proposal_uuid = kwargs.pop('proposal_uuid')
        super().__init__(*args, **kwargs)

        YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]
        self.fields['eligible'] = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
        self.fields['comment'] = forms.CharField(label='Comment<span class="asteriskField">*</span>', required=False,
                                                 max_length=1000,
                                                 help_text='Maximum length 1000 characters. Required if proposal is not eligible.',
                                                 widget=forms.Textarea(attrs={'rows': 4}))

        proposal = Proposal.objects.get(uuid=self._proposal_uuid)

        if proposal.eligibility == Proposal.ELIGIBLE:
            self.fields['eligible'].initial = True
        elif proposal.eligibility == Proposal.NOTELIGIBLE:
            self.fields['eligible'].initial = False

        self.fields['comment'].initial = proposal.eligibility_comment

        self.helper = FormHelper(self)
        self.helper.form_id = 'eligibility_form'
        self.helper.form_action = reverse('logged-proposal-eligibility-update', kwargs={'uuid': self._proposal_uuid})

        self.helper.layout = Layout(
            Div(
                Div('eligible')
            ),
            Div(
                Div('comment')
            ),
            FormActions(
                Submit('save', 'Save Eligibility'),
                HTML('<p></p>'),
                cancel_edit_button(reverse('logged-proposal-detail', kwargs={'uuid': proposal.uuid}))
            )
        )

    def clean(self):
        super().clean()

        if 'eligible' in self.cleaned_data and 'comment' in self.cleaned_data:
            if self.cleaned_data['eligible'] == 'False' and not self.cleaned_data['comment']:
                raise forms.ValidationError({'comment': 'Comment is mandatory if the proposal is not eligible'})

    def save_eligibility(self, user):
        if not user_is_in_group_name(user, settings.MANAGEMENT_GROUP_NAME):
            raise PermissionDenied()

        eligible = self.cleaned_data['eligible']
        comment = self.cleaned_data.get('comment', None)

        proposal = Proposal.objects.get(uuid=self._proposal_uuid)

        if eligible == 'True':
            proposal.eligibility = Proposal.ELIGIBLE
        else:
            proposal.eligibility = Proposal.NOTELIGIBLE

        proposal.eligibility_comment = comment

        proposal.save()
