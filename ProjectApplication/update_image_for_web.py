import os
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectApplication.settings')
import django
django.setup()

from grant_management.models import Medium
from ProjectApplication import settings


def run():
    for object in Medium.objects.all():
        if not object.file_web:
            object.save()


if __name__ == '__main__':
    run()
