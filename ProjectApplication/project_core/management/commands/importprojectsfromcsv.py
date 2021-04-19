import csv
import pprint

from django.core.management.base import BaseCommand

from project_core.models import PhysicalPerson, PersonPosition, PersonTitle, Gender, OrganisationName

# For pprinting dictionaries doesn't change the order
# in Python 3.7 this is needed, in Python 3.8 (or 3.9?)
# there is a better way passing a parameter to the
# pprint.pprint function
pprint.sorted = lambda arg, *a, **kw: arg


class Command(BaseCommand):
    help = 'Imports projects from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        print(csv_file_path)
        import_csv(csv_file_path)


def create_or_get_physical_person(first_name, surname, orcid, gender):
    gender = Gender.objects.get(name=gender)

    orcid = orcid if orcid != '' else None

    physical_person, created = PhysicalPerson.objects.get_or_create(first_name=first_name,
                                                                    surname=surname,
                                                                    orcid=orcid,
                                                                    gender=gender)

    return physical_person


def get_call_short_name(short_name):
    pass


def create_installment(date, amount):
    pass


def create_invoice(received, sent_for_payment, paid, amount, url):
    pass


def create_project(person_position, installments, invoices):
    pass


def create_financial_report(received, sent_for_approval, approval_date, approved_by, url):
    pass


def create_scientific_report(received, sent_for_approval, approval_date, approved_by, url):
    pass


def filter_dictionary(dictionary, starts_with):
    ignore_chars = len(starts_with)
    return {key[ignore_chars:]: dictionary[key] for key in dictionary if key.startswith(starts_with)}


def get_person_title(title):
    return PersonTitle.objects.get(title=title)

def create_or_get_organisation_names(organisation_names_str):
    organisation_names = []

    for organisation_name_str in organisation_names_str:
        organisation_name_obj, created = OrganisationName.objects.get_or_create(name=organisation_name_str)
        organisation_names.append(organisation_name_obj)

    return organisation_names

def create_or_get_person_position(person_position_info):
    physical_person = create_or_get_physical_person(person_position_info['person__first_name'],
                                                    person_position_info['person__surname'],
                                                    person_position_info['person__orcid'],
                                                    person_position_info['person__gender'],
                                                    )

    academic_title = get_person_title(person_position_info['person__academic_title'])

    organisation_names = create_or_get_organisation_names(person_position_info['organisation_names'])

    person_position, created = PersonPosition.objects.get_or_create(person=physical_person,
                                                                    academic_title=academic_title,
                                                                    # organisation_names=organisation_names, TODO
                                                                    group=person_position_info['person__group'])
    return person_position


def import_csv(csv_file_path):
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file)

        transposed = zip(*csv_reader)

        headers = next(transposed)

        projects = []
        for row in transposed:
            projects.append(dict(zip(headers, row)))

        pprint.pprint(projects)

        for project in projects:
            principal_investigator_information = filter_dictionary(project, 'principal_investigator__')
            principal_investigator = create_or_get_person_position(principal_investigator_information)
            print(principal_investigator)
