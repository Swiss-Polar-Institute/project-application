from crispy_forms.helper import FormHelper
from django import forms
from django.forms import Form


class DataCollectionForm(Form):
    def __init__(self, *args, **kwargs):
        person_position = kwargs.pop('person_position', None)

        super().__init__(*args, **kwargs)

        privacy_policy_initial = contact_newsletter_initial = None

        if person_position:
            privacy_policy_initial = person_position.privacy_policy
            contact_newsletter_initial = person_position.contact_newsletter

        self.fields['privacy_policy'] = forms.BooleanField(initial=privacy_policy_initial,
                                                           help_text='By ticking this box you agree to the Swiss Polar Insitute (SPI) storing your '
                                                                  'personal data for the purpose of administering your '
                                                                  'proposal. The data you provide here will be kept private and '
                                                                  'held securely by the SPI according '
                                                                  'to the <a href="https://cipd.epfl.ch/en/privacy-policy/">EPFL Privacy Policy</a>. '
                                                                  'Anonymised statistics will be produced about the proposal applications. '
                                                                  'If your proposal is selected for funding, your data will also be used '
                                                                  'for the administration of your project and may contribute to '
                                                                  'scientific metadata for the project.',
                                                           label='I agree to my personal data being saved by SPI for the administration of my proposal')

        self.fields['contact_newsletter'] = forms.BooleanField(initial=contact_newsletter_initial,
                                                               help_text='By ticking this box you agree to being contacted '
                                                                  'by SPI with news and future opportunities. '
                                                                  'Your contact details will not be used for other purposes.',
                                                               required=False,
                                                               label='I would like to receive SPI news and future opportunities')

        self.helper = FormHelper(self)
        self.helper.form_tag = False

    def update(self, person_position):
        person_position.privacy_policy = self.cleaned_data['privacy_policy']
        person_position.contact_newsletter = self.cleaned_data['contact_newsletter']
        person_position.save()