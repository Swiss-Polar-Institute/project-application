from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django.forms import ModelForm

from ..models import PostalAddress, Country


class PostalAddressApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self._all_fields_are_optional = kwargs.pop('all_fields_are_optional', True)
        super().__init__(*args, **kwargs)

        self.fields['address'].widget.attrs['rows'] = 7
        self.fields['country'].queryset = self.fields['country'].queryset.order_by('name')
        self.fields['country'].initial = Country.objects.get(name='Switzerland')

        if self._all_fields_are_optional:
            for field in self.fields.values():
                field.required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div('address', css_class='col-6'),
                Div('city', 'postcode', 'country', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        super().clean()

    def save(self, commit=True):
        return super().save(commit=True)

    class Meta:
        model = PostalAddress
        fields = ['address', 'city', 'postcode', 'country']
        help_texts = {
            'address': 'Please enter the professional postal address to which correspondence related to this proposal can be sent. Correspondence will be addressed to the applicant'}
        labels = {'address': 'Professional postal address*', 'city': 'City*', 'postcode': 'Postcode*', 'country': 'Country*' }
