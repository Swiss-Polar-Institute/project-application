from django import forms
from django.template import loader
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from project_core.models import SpiUser


class UserCreationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])

        email_message.send()

    def _post_clean(self):
        super()._post_clean()

    def save(self, *args, **kwargs):
        user: SpiUser = super().save(*args, **kwargs)
        subject_template_name = 'registration/register_subject.txt'
        email_template_name = 'registration/register_email.html'

        SpiUser.set_type_of_user(user, settings.APPLICANT_GROUP_NAME)
        new_password = User.objects.make_random_password()
        user.password = make_password(new_password)
        user.save()
        context = {
            'email': user.email,
            'site_name': "SwissPolar Institute",
            'username': user.username,
            'password': new_password
        }
        self.send_mail(subject_template_name, email_template_name, context, settings.DEFAULT_FROM_EMAIL, user.email)

        return user
