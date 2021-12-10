from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from dal import autocomplete
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe

from evaluation.models import Reviewer
from project_core.forms.utils import cancel_edit_button, cancel_button
from project_core.models import SpiUser, PhysicalPerson
from project_core.utils.utils import new_person_message


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial_type_of_user = kwargs.pop('type_of_user', None)

        super().__init__(*args, **kwargs)

        self.new_password = None
        self.user_id_new_password = None

        self.helper = FormHelper(self)

        self.fields['type_of_user'] = forms.ChoiceField(required=True,
                                                        choices=[(settings.MANAGEMENT_GROUP_NAME, 'Management'),
                                                                 (settings.REVIEWER_GROUP_NAME, 'Reviewer'),
                                                                 ],
                                                        widget=forms.RadioSelect,
                                                        help_text='Reviewers only have access to proposals. Management users have access to everything in Nestor'
                                                        )

        self._is_edit_action = bool(self.instance.id)
        self._is_create_action = not self._is_edit_action

        if self._is_edit_action:
            self._original_username = self.instance.username
        else:
            self._original_username = None

        initial_physical_person = None

        reviewer = None

        if self._is_edit_action:
            cancel_html = cancel_edit_button(reverse('logged-user-detail', kwargs={'pk': self.instance.id}))

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

        else:
            self.fields['is_active'].required = True
            self.fields['is_active'].initial = True
            self.fields['is_active'].disabled = True
            cancel_html = cancel_button(reverse('logged-user-list'))

        if initial_type_of_user:
            self.fields['type_of_user'].initial = initial_type_of_user

        used_users = list(Reviewer.objects.all().values_list('person', flat=True))

        if self.instance and self.instance.id:
            my_user = self.instance
            reviewer = Reviewer.objects.filter(user=my_user).first()
            # It might exist because the User might have been previously a reviewer and then changed to management
            if reviewer:
                my_physical_person_id = reviewer.user_id
            else:
                my_physical_person_id = 0

        if reviewer:
            initial_physical_person = reviewer.person
            used_users.remove(initial_physical_person.id)
            my_physical_person_id = initial_physical_person.id

        list_users_url = reverse('logged-user-list')
        self.fields['physical_person'] = forms.ModelChoiceField(
            label='Person<span class="asteriskField">*</span>',
            required=False,
            help_text=f"Choose the reviewer's name from the list{new_person_message()}.<br>"
                      f"To give access to different calls add the reviewer to the Call Evaluation.",
            queryset=PhysicalPerson.objects.all().exclude(id__in=used_users),
            initial=initial_physical_person,
            widget=autocomplete.ModelSelect2(url=reverse(
                'logged-autocomplete-physical-people-non-reviewers') + f'?force_include={my_physical_person_id}'))

        self.fields['generate_new_password'] = forms.BooleanField(required=self._is_create_action,
                                                                  disabled=self._is_create_action,
                                                                  initial=self._is_create_action,
                                                                  help_text='If enabled, a new password will be generated for this user. If editing a user, this option can be used to change a forgotten password')

        self.helper.layout = Layout(
            Div(
                Div('username', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('type_of_user', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('physical_person', css_class='col-6'),
                css_class='row reviewer_information',
            ),
            Div(
                Div('first_name', css_class='col-6'),
                Div('last_name', css_class='col-6'),
                css_class='row management_information',
            ),
            Div(
                Div('is_active', css_class='col-6'),
                Div('generate_new_password', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save User'),
                cancel_html
            )
        )

    def clean_username(self):
        username = self.cleaned_data['username']

        duplicated_error = 'Username already exists. Please use another one'

        if self._is_create_action and User.objects.filter(username=username).exists():
            raise forms.ValidationError(duplicated_error)

        if self._is_edit_action and User.objects.filter(
                username=username).exists() and self._original_username != username:
            raise forms.ValidationError(duplicated_error)

        return username

    def clean(self):
        if self.cleaned_data.get('type_of_user', '') == settings.REVIEWER_GROUP_NAME:
            physical_person = self.cleaned_data['physical_person']
            if physical_person is None:
                raise forms.ValidationError(
                    {'physical_person': 'Person is mandatory if the type of user is a reviewer'})
            else:
                user = User.objects.filter(username=self.cleaned_data['username']).first()

                another_reviewer_same_user = Reviewer.objects.filter(person=physical_person). \
                    exclude(user=user). \
                    first()

                if another_reviewer_same_user:
                    raise forms.ValidationError(
                        {'username': mark_safe(
                            f'{another_reviewer_a_href(another_reviewer_same_user)} exist with this username')}
                    )

                if user:
                    duplicate = Reviewer.objects.filter(person=physical_person).exclude(user=user).exists()

                    if duplicate:
                        raise forms.ValidationError(
                            {'physical_person': 'This physical person is assigned to another reviewer'})

    def save(self, *args, **kwargs):
        user: SpiUser = super().save(*args, **kwargs)

        # At this point user is a User object, not SpiUser

        physical_person: PhysicalPerson = self.cleaned_data.get('physical_person')

        SpiUser.set_type_of_user(user, self.cleaned_data['type_of_user'], physical_person)

        if self.cleaned_data['type_of_user'] == settings.REVIEWER_GROUP_NAME:
            user.first_name = ''
            user.last_name = ''
            user.save()
        elif self.cleaned_data['type_of_user'] == settings.MANAGEMENT_GROUP_NAME:
            pass
        else:
            assert False

        if self.cleaned_data['generate_new_password']:
            self.new_password = User.objects.make_random_password()
            self.user_id_new_password = user.id
            # The password is set on the view to allow the user to see
            # the new password (since user.set_password logs out the user)
            # This is to allow users to reset their own passwords
            # user.set_password(self.new_password)
            # user.save()

        return user

    class Meta:
        model = SpiUser
        fields = ['username', 'first_name', 'last_name', 'is_active']
        help_texts = {
            'is_active': 'Designates whether this user should be treated as active. Untick this box instead of deleting accounts for inactive users'}


def another_reviewer_a_href(reviewer):
    link = reverse("logged-user-detail", kwargs={"pk": reviewer.user_id})

    return f'<a href="{link}">Another reviewer</a>'
