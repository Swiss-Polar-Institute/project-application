from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from dal import autocomplete
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from evaluation.models import Reviewer
from project_core.forms.utils import cancel_edit_button
from project_core.models import SpiUser, PhysicalPerson


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial_type_of_user = kwargs.pop('type_of_user', None)

        super().__init__(*args, **kwargs)

        self.new_password = None
        self.user_id_new_password = None

        self.helper = FormHelper(self)

        cancel_edit_url = reverse('logged-user-list')

        self.fields['type_of_user'] = forms.ChoiceField(required=True,
                                                        choices=[(settings.MANAGEMENT_GROUP_NAME, 'Management'),
                                                                 (settings.REVIEWER_GROUP_NAME, 'Reviewer'),
                                                                 ],
                                                        widget=forms.RadioSelect,
                                                        help_text='Reviewers only have access to proposals. Management users have access to everything in Nestor'
                                                        )

        edit_action = self.instance.id
        create_action = not edit_action

        initial_physical_person = None

        reviewer = None

        if edit_action:
            group_count = 0
            if self.instance.groups.filter(name=settings.REVIEWER_GROUP_NAME).exists():
                self.fields['type_of_user'].initial = settings.REVIEWER_GROUP_NAME

                try:
                    reviewer = Reviewer.objects.get(user=self.instance)
                except Reviewer.DoesNotExist:
                    pass

                if reviewer:
                    initial_physical_person = reviewer.person

                group_count += 1
            if self.instance.groups.filter(name=settings.MANAGEMENT_GROUP_NAME).exists():
                self.fields['type_of_user'].initial = settings.MANAGEMENT_GROUP_NAME
                group_count += 1

            assert group_count < 2, 'A user cannot be a reviewer and management at the same time'

        if initial_type_of_user:
            self.fields['type_of_user'].initial = initial_type_of_user

        used_users = list(Reviewer.objects.all().values_list('person', flat=True))

        my_physical_person_id = 0

        if reviewer:
            initial_physical_person = reviewer.person
            used_users.remove(initial_physical_person.id)
            my_physical_person_id = initial_physical_person.id

        new_person_url = reverse('logged-person-position-add')
        list_users_url = reverse('logged-user-list')
        self.fields['physical_person'] = forms.ModelChoiceField(
            label='Person<span class="asteriskField">*</span>',
            required=False,
            help_text="Choose the reviewer's name from the list. Only people that have accepted the "
                      f'policy privacy and that are not yet a reviewer, are displayed. If you think the person may '
                      f'already be a reviewer, <a href="{list_users_url}">check the list of users</a> before creating another. '
                      f'If they are not listed, <a href="{new_person_url}">create a new person</a> then reload this page.',
            queryset=PhysicalPerson.objects.all().exclude(id__in=used_users),
            initial=initial_physical_person,
            widget=autocomplete.ModelSelect2(url=reverse(
                'logged-autocomplete-physical-people-non-reviewers') + f'?force_include={my_physical_person_id}'))

        self.fields['generate_new_password'] = forms.BooleanField(required=create_action,
                                                                disabled=create_action,
                                                                initial=create_action,
                                                                help_text='If enabled, a new password will be generated for this user. If editing a user, this option can be used to change a forgotten password')

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
                Div('physical_person', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('is_active', css_class='col-6'),
                Div('generate_new_password', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save User'),
                cancel_edit_button(cancel_edit_url)
            )
        )

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists. Pleas use another one')

        return username

    def clean(self):
        if self.cleaned_data.get('type_of_user', '') == settings.REVIEWER_GROUP_NAME and \
                self.cleaned_data['physical_person'] is None:
            raise forms.ValidationError({'comment': 'Person is mandatory if the type of user is a reviewer'})

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)

        # At this point user is a User object, not SpiUser

        physical_person = self.cleaned_data.get('physical_person')

        SpiUser.set_type_of_user(user, self.cleaned_data['type_of_user'], physical_person)

        if self.cleaned_data['generate_new_password']:
            self.new_password = User.objects.make_random_password()
            self.user_id_new_password = user.id
            user.set_password(self.new_password)
            user.save()

        return user

    class Meta:
        model = SpiUser
        fields = ['username', 'first_name', 'last_name', 'is_active']
        help_texts = {
            'is_active': 'Designates whether this user should be treated as active. Untick this box instead of deleting accounts for inactive users'}
