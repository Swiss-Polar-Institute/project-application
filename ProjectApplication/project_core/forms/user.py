from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.contrib.auth.models import User
from django.urls import reverse

from project_core.forms.utils import cancel_edit_button


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        cancel_edit_url = reverse('logged-user-list')

        self.fields['create_new_password'] = forms.BooleanField(required=False,
                                                                help_text='If enabled it will generate and display a new password for the user')

        self.helper.layout = Layout(
            Div(
                Div('username', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('first_name', css_class='col-6'),
                Div('last_name', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('is_active', css_class='col-6'),
                Div('create_new_password', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save User'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)

        if self.cleaned_data['create_new_password']:
            password = User.objects.make_random_password()
            user.password = password
            user.save()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_active']
