import csv
import os
import pprint
import subprocess
from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from grant_management.models import GrantAgreement
from project_core.models import PhysicalPerson, PersonPosition, PersonTitle, Gender, OrganisationName, Project, Call, \
    Contact, GeographicalArea, Keyword, Source, KeywordUid

# This is a throw away script to import past data

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
    if gender:
        gender = Gender.objects.get(name=gender)

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
        organisation_name_str = organisation_name_str.strip()
        organisation_name_obj, created = OrganisationName.objects.get_or_create(name=organisation_name_str)
        organisation_names.append(organisation_name_obj)

    organisation_names.sort(key=lambda o: o.id)

    return organisation_names


def create_or_get_person_position(person_position_info):
    physical_person = create_or_get_physical_person(person_position_info['person__first_name'],
                                                    person_position_info['person__surname'],
                                                    person_position_info['person__orcid'],
                                                    person_position_info['person__gender'],
                                                    )

    academic_title = get_person_title(person_position_info['academic_title'])

    organisation_names = create_or_get_organisation_names(person_position_info['organisation_names'])

    person_position_specific_info = {'person': physical_person,
                                     'academic_title': academic_title,
                                     'group': person_position_info['person__group']
                                     }
    person_positions = PersonPosition.objects.filter(**person_position_specific_info)

    found = False
    person_position = None
    for person_position in person_positions:
        person_position_organisation_names = list(person_position.organisation_names.all())
        person_position_organisation_names.sort(key=lambda o: o.id)

        if person_position_organisation_names == organisation_names and \
                person_position.main_email() == person_position_info['email']:
            found = True
            break

    if not found:
        person_position = PersonPosition.objects.create(**person_position_specific_info)
        person_position.organisation_names.add(*organisation_names)

        Contact.objects.get_or_create(person_position=person_position,
                                      entry=person_position_info['email'],
                                      method=Contact.EMAIL)

    assert person_position

    return person_position


def dictionary_strings_to_types(dictionary):
    # Cast to int, floats, lists, eates... and no more (no database lookups)

    result = {}

    for key, value in dictionary.items():
        if value == '':
            result[key] = None
            continue

        try:
            value_int = int(value)
            result[key] = value_int
            continue
        except ValueError:
            pass

        try:
            value_float = float(value)
            result[key] = value_float
            continue
        except ValueError:
            pass

        try:
            value_date = datetime.strptime(value, '%d-%m-%Y')
            result[key] = value_date
            continue
        except ValueError:
            pass

        if key in ['keywords', 'principal_investigator__organisation_names', 'geographical_areas']:
            value_list = value.split(',')
            value_list = [value_element.strip() for value_element in value_list]
            result[key] = value_list
            continue

        # It's a string
        result[key] = value

    return result


def create_project(project_data, principal_investigator):
    call = Call.objects.get(short_name=project_data['call__short_name'])
    assert project_data['status'] in [Project.ONGOING, Project.COMPLETED, Project.ABORTED]

    project = Project.objects.create(title=project_data['title'],
                                     key=project_data['key'],
                                     principal_investigator=principal_investigator,
                                     location=project_data['location'],
                                     start_date=project_data['start_date'],
                                     end_date=project_data['end_date'],
                                     call=call,
                                     allocated_budget=project_data['allocated_budget'],
                                     status=project_data['status'],
                                     closed_on=project_data['end_date'],  # TODO: is this correct?
                                     closed_by=None,  # TODO: should we create a new data import user?
                                     )

    return project


def set_geographical_areas(project, geographical_areas):
    for geographical_area_str in geographical_areas:
        geographical_area = GeographicalArea.objects.get(name=geographical_area_str)
        project.geographical_areas.add(geographical_area)


def set_keywords(project, keywords):
    for keyword_str in keywords:
        source, created = Source.objects.get_or_create(source='Importer of old projects')

        keyword_uuid, created = KeywordUid.objects.get_or_create(uid=None, source=source)

        keyword, created = Keyword.objects.get_or_create(name=keyword_str, defaults={'uid': keyword_uuid})

        project.keywords.add(keyword)


def content_type_from_file_name(file_name):
    file_name_lower = file_name.lower()

    if file_name_lower.endswith('.docx'):
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml'
    elif file_name_lower.endswith('.pdf'):
        return 'application/pdf'
    elif file_name_lower.endswith('.eml'):
        return 'message/rfc822'
    elif file_name_lower.endswith('.msg'):
        return 'application/vnd.ms-outlook'
    elif file_name_lower.endswith('jpg'):
        return 'image/jpeg'

    assert False


def set_grant_agreement(project, grant_agreement_information):
    file_path = grant_agreement_information['file_path']

    rclone = subprocess.run(['rclone', 'cat', file_path], capture_output=True)

    assert rclone.returncode == 0

    file_contents = rclone.stdout

    file = SimpleUploadedFile(content=file_contents, name=os.path.basename(file_path),
                              content_type=content_type_from_file_name(file_path))

    GrantAgreement.objects.create(project=project,
                                  file=file)


def import_csv(csv_file_path):
    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)

        transposed = zip(*csv_reader)

        headers = next(transposed)

        projects = []
        for row in transposed:
            projects.append(dict(zip(headers, row)))

        pprint.pprint(projects)

        for project_data in projects:
            project_data = dictionary_strings_to_types(project_data)
            principal_investigator_information = filter_dictionary(project_data, 'principal_investigator__')
            principal_investigator = create_or_get_person_position(principal_investigator_information)

            project = create_project(project_data, principal_investigator)

            set_geographical_areas(project, project_data['geographical_areas'])
            set_keywords(project, project_data['keywords'])

            grant_agreement_information = filter_dictionary(project_data, 'grant_agreement__')
            set_grant_agreement(project, grant_agreement_information)
