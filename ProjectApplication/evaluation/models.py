from django.contrib.auth.models import User
from django.db import models

from project_core.models import Call
from project_core.templatetags.user_is_reviewer import user_is_reviewer


class Reviewer(models.Model):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    calls = models.ManyToManyField(Call, blank=True)

    def __str__(self):
        calls = ', '.join([str(call) for call in self.calls.all()])
        return f'R: {self.user} C: {calls}'

    @staticmethod
    def filter_proposals(proposals, user):
        if user_is_reviewer(user):
            reviewer = Reviewer.objects.get(user=user)
            return proposals.filter(call__in=reviewer.calls.all())
