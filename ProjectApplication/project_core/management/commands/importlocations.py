import csv
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.transaction import set_autocommit, commit

from grant_management.models import Location
from project_core.models import Project


class Command(BaseCommand):
    help = 'Import locations of projects'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        self._import_data_from_csv(options['filename'])

    def _import_data_from_csv(self, filename):
        set_autocommit(False)

        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)

            # user = User.objects.get(username='data.importer')

            for row in reader:
                print('Importing', row['key'])

                project = Project.objects.get(key=row['key'])

                self._import_locations(project, row)

        commit()

    def _import_locations(self, project, row):
        i = 1
        while f'lat-long{i}' in row:
            lat_long = row[f'lat-long{i}']
            if lat_long != '':
                latitude, longitude = lat_long.split(',')

                latitude = Decimal(latitude)
                longitude = Decimal(longitude)

                Location.objects.get_or_create(
                    project=project,
                    name=row[f'name_location{i}'],
                    defaults={'latitude': latitude,
                              'longitude': longitude})

            i += 1
