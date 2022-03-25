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
            url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{settings.AWS_LOCATION}/{object.file}"
            response = requests.get(url)
            if response.status_code == 200:
                object.save()


if __name__ == '__main__':
    run()
