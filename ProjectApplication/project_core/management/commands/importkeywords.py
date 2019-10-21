# This code is modified from Pina Estany, Carles, & Thomas, Jenny. (2019, August 5). Swiss-Polar-Institute/science-cruise-data-management v0.1.0 (Version 0.1.0). Zenodo. http://doi.org/10.5281/zenodo.3360649
# Also available at: https://github.com/Swiss-Polar-Institute/science-cruise-data-management

from django.core.management.base import BaseCommand
from django.utils import timezone

from project_core.models import Keyword, Source
import csv


class Command(BaseCommand):
    help = 'Adds Keywords from GCMD file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('source', type=str)

    def handle(self, *args, **options):
        importer = KeywordsImporter(options['filename'], options['source'])

        importer.import_keywords()


class KeywordsImporter:
    def __init__(self, file_path:str, source_name: str):
        self._file_path = file_path
        self._source_name = source_name

    def import_keywords(self):
        source = KeywordsImporter.get_source(self._source_name)
        KeywordsImporter.import_file(self._file_path, source)

    @staticmethod
    def get_source(source_name):
        source, created = Source.objects.get_or_create(source=source_name, defaults={'source': source_name})
        return source

    @staticmethod
    def import_file(file_path: str, source):
        with open(file_path) as csvfile:
            reader = csv.reader(csvfile)

            next(reader) # The file has a header not part of the CSV
            next(reader) # Ignores the file normal header

            for row in reader:
                column = min(4, len(row))

                while row[column] == '':
                    column -= 1

                keyword_str = row[column]

                keyword = Keyword()
                keyword.name = keyword_str.lower()
                keyword.source = source

                keyword.save()