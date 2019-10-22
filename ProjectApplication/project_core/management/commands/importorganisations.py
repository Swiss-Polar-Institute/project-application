# This code is modified from Pina Estany, Carles, & Thomas, Jenny. (2019, August 5). Swiss-Polar-Institute/science-cruise-data-management v0.1.0 (Version 0.1.0). Zenodo. http://doi.org/10.5281/zenodo.3360649
# Also available at: https://github.com/Swiss-Polar-Institute/science-cruise-data-management

from django.core.management.base import BaseCommand
from django.utils import timezone

from project_core.models import Organisation, Country, Source, OrganisationUid
import csv


class Command(BaseCommand):
    help = 'Adds vocabulary list to the organisation table'

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
            organisation_uid, created = OrganisationUid.objects.get_or_create(uid=None, source=source)

            for row in reader:
                organisation = Organisation()
                organisation.long_name = row['long_name']
                organisation.short_name = row['short_name']
                organisation.street = row['street']
                organisation.city = row['city']
                organisation.postal_code = row['postal_code']
                organisation.country = Country.objects.get(name=row['country'])
                organisation.uid = organisation_uid
                organisation.save()
