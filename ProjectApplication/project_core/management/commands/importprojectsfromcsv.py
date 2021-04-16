import csv
import pprint

from django.core.management.base import BaseCommand

# So pprinting dictionaries doesn't change the order
pprint.sorted = lambda arg, *a, **kw: arg


class Command(BaseCommand):
    help = 'Imports projects from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        print(csv_file_path)
        import_csv(csv_file_path)


def create_or_get_physical_person(first_name, surname, orcid):
    pass


def create_or_get_person_position(physical_person, gender, academic_title, organisation_names, group):
    pass


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


def import_csv(csv_file_path):
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file)

        transposed = zip(*csv_reader)

        print(transposed)

        headers = next(transposed)

        projects = []
        for row in transposed:
            projects.append(dict(zip(headers, row)))

        pprint.pprint(projects)

        for project in projects:
            print(project['title'])
