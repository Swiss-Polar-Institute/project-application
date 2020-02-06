from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse



class EligibilityDecisionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        proposal_uuid = kwargs.pop('proposal_uuid')
        super().__init__(*args, **kwargs)

        YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]
        self.fields['eligible'] = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
        self.fields['comment'] = forms.CharField(label='Comment', max_length=1000,
                                                 widget=forms.Textarea(attrs={'rows': 4}))

        self.helper = FormHelper(self)
        self.helper.form_action = reverse('logged-proposal-eligibility-update', kwargs={'uuid': proposal_uuid})
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.layout = Layout(
            Div(
                Div('eligible')
            ),
            Div(
                Div('comment')
            )
        )
