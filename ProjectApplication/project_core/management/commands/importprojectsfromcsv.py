from django.core.management.base import BaseCommand
import csv
import pprint

pprint.sorted = lambda arg, *a, **kw: arg

from project_core.models import *

phd_student = CareerStage.objects.get(name='PhD student')
mx = PersonTitle.objects.get(title='Mx')


class Command(BaseCommand):
    help = 'Imports projects from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        print(csv_file_path)
        import_csv(csv_file_path)

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
