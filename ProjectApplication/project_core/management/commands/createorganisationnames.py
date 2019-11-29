from django.core.management.base import BaseCommand

from project_core.models import Organisation, OrganisationName


class Command(BaseCommand):
    help = 'Adds vocabulary list to the country table'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        organisation_names = CreateOrganisationNames()
        organisation_names.create()


class CreateOrganisationNames:
    def __init__(self):
        pass

    def create(self):
        for organisation in Organisation.objects.all():
            name = organisation.long_name
            if organisation.short_name:
                name += ' - ' + organisation.short_name
            organisation_name, created = OrganisationName.objects.get_or_create(name=name)
            organisation_name.organisation = organisation
            organisation_name.save()
