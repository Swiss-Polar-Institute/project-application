from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from project_core.forms.utils import cancel_edit_button
from project_core.models import SpiUser


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial_type_of_user = kwargs.pop('type_of_user', None)

        super().__init__(*args, **kwargs)

        self.new_password = None

        self.helper = FormHelper(self)

        cancel_edit_url = reverse('logged-user-list')

        self.fields['type_of_user'] = forms.ChoiceField(required=True,
                                                        choices=[(settings.MANAGEMENT_GROUP_NAME, 'Management'),
                                                                 (settings.REVIEWER_GROUP_NAME, 'Reviewer'),
                                                                 ],
                                                        widget=forms.RadioSelect,
                                                        help_text='Reviewers have access to only proposals. Management to everything in Nestor'
                                                        )

        if self.instance.id:
            group_count = 0
            if self.instance.groups.filter(name=settings.REVIEWER_GROUP_NAME).exists():
                self.fields['type_of_user'].initial = settings.REVIEWER_GROUP_NAME
                group_count += 1
            if self.instance.groups.filter(name=settings.MANAGEMENT_GROUP_NAME).exists():
                self.fields['type_of_user'].initial = settings.MANAGEMENT_GROUP_NAME
                group_count += 1

            assert group_count < 2, 'A user cannot be a reviewer and management at the same time'

        if initial_type_of_user:
            self.fields['type_of_user'].initial = initial_type_of_user

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
                Div('type_of_user', css_class='col-6'),
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

        # At this point user is a User object, not SpiUser

        SpiUser.set_type_of_user(user, self.cleaned_data['type_of_user'])

        if self.cleaned_data['create_new_password']:
            self.new_password = User.objects.make_random_password()
            user.set_password(self.new_password)
            user.save()

        return user

    class Meta:
        model = SpiUser
        fields = ['username', 'first_name', 'last_name', 'is_active']
