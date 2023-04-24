import requests
import filetype

from django.core.management.base import BaseCommand
from grant_management.models import Medium


class Command(BaseCommand):
    help = 'Upload all media to the spi media gallery'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        url = "https://media.swisspolar.ch/api/v1/medium/"
        for medium in Medium.objects.all():
            if medium.tags.exists() and not medium.uploaded:
                data = {}
                files = {'file': medium.file.open()}
                if filetype.is_image(files['file']):
                    data["medium_type"] = "P"
                elif filetype.is_video(files['file']):
                    data["medium_type"] = "V"
                else:
                    print("Unsupported file type")
                    continue
                data["project"] = f"SPI project/{medium.project.key.split('-')[0]}"
                data["photographer_value"] = str(medium.photographer)
                data["location_value"] = f"Location/{medium.project.location}"
                data["copyright"] = str(medium.copyright)
                data["license"] = str(medium.license)
                data["datetime_taken"] = medium.received_date.strftime('%Y-%m-%d')
                tagstr = ""
                for tag in medium.tags.all():
                    tagstr += f"{tag},"
                data["tags_value"] = tagstr[:-1]
                response = requests.post(url, data=data, files=files)
                if response.status_code == 201:
                    medium.uploaded = True
                    medium.save()
                    print("Medium uploaded")
