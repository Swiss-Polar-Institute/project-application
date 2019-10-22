# This code is modified from Pina Estany, Carles, & Thomas, Jenny. (2019, August 5). Swiss-Polar-Institute/science-cruise-data-management v0.1.0 (Version 0.1.0). Zenodo. http://doi.org/10.5281/zenodo.3360649
# Also available at: https://github.com/Swiss-Polar-Institute/science-cruise-data-management

from django.core.management.base import BaseCommand

from project_core.models import Country, Source, CountryUid
import csv


class Command(BaseCommand):
    help = 'Adds vocabulary list to the country table'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('source', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'], options['source'])

    def import_data_from_csv(self, filename, source_name):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)

            source, created = Source.objects.get_or_create(source=source_name)
            country_uid, created = CountryUid.objects.get_or_create(uid=None, source=source)

            for row in reader:
                country = Country()
                country.name = row['preflabel']
                country.uid = country_uid
                country.save()
