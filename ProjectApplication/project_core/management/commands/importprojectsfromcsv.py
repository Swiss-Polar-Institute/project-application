import csv
import os
import pprint
import subprocess
import urllib.parse
from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from comments.models import ProjectComment, ProjectCommentCategory, Category
from grant_management.models import GrantAgreement, Installment, Invoice, FinancialReport, ScientificReport
from project_core.models import PhysicalPerson, PersonPosition, PersonTitle, Gender, OrganisationName, Project, Call, \
    Contact, GeographicalArea, Keyword, Source, KeywordUid
# For pprinting dictionaries doesn't change the order
# in Python 3.7 this is needed, in Python 3.8 (or 3.9?)
# there is a better way passing a parameter to the
# pprint.pprint function
from project_core.templatetags.thousands_separator import thousands_separator
# This is a throw away script to import past data
from project_core.utils.utils import format_date

pprint.sorted = lambda arg, *a, **kw: arg


class Command(BaseCommand):
    help = 'Imports projects from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        print(csv_file_path)
        import_csv(csv_file_path)


def create_or_get_physical_person(first_name, surname, orcid=None, gender=None):
    if gender:
        gender = Gender.objects.get(name=gender)

    if orcid:
        physical_person, created = PhysicalPerson.objects.get_or_create(orcid=orcid,
                                                                        defaults={'first_name': first_name,
                                                                                  'surname': surname,
                                                                                  'gender': gender
                                                                                  })
    else:
        first_name_surname_before_count = PhysicalPerson.objects.filter(first_name=first_name, surname=surname).count()

        physical_person, created = PhysicalPerson.objects.get_or_create(first_name=first_name,
                                                                        surname=surname,
                                                                        defaults={'gender': gender})

        # It didn't exist and it got created or it existed and didn't get created
        assert first_name_surname_before_count == 0 and created or first_name_surname_before_count > 0 and not created

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
        if key == 'keywords' and value == '':
            result[key] = []
            continue

        if value in ('', None):
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

        try:
            value_date = datetime.strptime(value, '%d/%m/%Y')
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

    if project_data['status'] in [Project.COMPLETED, Project.ABORTED]:
        assert project_data['closed_date']

    project_key = f'ACE-2016-{project_data["key"]:03}'

    allocated_budget_chf = project_data['allocated_budget_chf']
    allocated_budget_eur = project_data['allocated_budget_eur']

    project = Project.objects.create(title=project_data['title'],
                                     key=project_key,
                                     principal_investigator=principal_investigator,
                                     location=project_data['location'],
                                     start_date=project_data['start_date'],
                                     end_date=project_data['end_date'],
                                     call=call,
                                     allocated_budget=allocated_budget_chf,
                                     status=project_data['status'],
                                     closed_on=project_data['closed_date'],  # TODO: is this correct?
                                     closed_by=None,  # TODO: should we create a new data import user?
                                     )

    comment_text = f"This project's finance was originally in Euros\n\n" \
                   f"Allocated budget in Euros: {thousands_separator(allocated_budget_eur)} EUR\n\n"

    category = Category.objects.get(name='Finance')
    category = ProjectCommentCategory.objects.get(category=category)
    ProjectComment.objects.create(project=project, category=category, text=comment_text)

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


def create_simple_uploaded_file(file_path):
    if file_path is None:
        return None

    file_path = file_path[len('https://swisspolar.sharepoint.com/sites/S/S/'):]

    file_path = urllib.parse.unquote(file_path)

    file_path = 'Commun-SwissPolar:' + file_path

    rclone_process = subprocess.run(['rclone', 'cat', file_path], capture_output=True)

    assert rclone_process.returncode == 0

    file_contents = rclone_process.stdout

    return SimpleUploadedFile(content=file_contents, name=os.path.basename(file_path),
                              content_type=content_type_from_file_name(file_path))


def set_grant_agreement(project, grant_agreement_information):
    file = create_simple_uploaded_file(grant_agreement_information['file'])

    grant_agreement = GrantAgreement.objects.create(project=project,
                                                    signed_date=grant_agreement_information['signed_date'],
                                                    file=file)

    index = 1
    while f'signed_by_{index}_first_name' in grant_agreement_information:
        signed_by_first_name = grant_agreement_information[f'signed_by_{index}_first_name']
        signed_by_surname = grant_agreement_information[f'signed_by_{index}_surname']

        index += 1

        if signed_by_first_name is None:
            continue

        physical_person, created = PhysicalPerson.objects.get_or_create(first_name=signed_by_first_name,
                                                                        surname=signed_by_surname)
        grant_agreement.signed_by.add(physical_person)


def set_installments(project, installments_data):
    index = 1

    while f'{index}_amount_chf' in installments_data:
        amount = installments_data[f'{index}_amount_chf']
        if amount is None:
            break

        assert amount
        assert amount > 0
        assert amount <= project.allocated_budget

        Installment.objects.create(project=project,
                                   amount=amount)

        index += 1


def set_invoices(project, invoices_data):
    index = 1

    comments = []

    while f'{index}_received_date' in invoices_data:
        received_date = invoices_data[f'{index}_received_date']
        if received_date is None:
            break

        installment_number = index
        installment = Installment.objects.filter(project=project).order_by('id')[index - installment_number]

        file = create_simple_uploaded_file(invoices_data[f'{index}_file'])

        amount_chf = invoices_data[f'{index}_amount_chf']
        amount_eur = invoices_data[f'{index}_amount_eur']

        assert amount_chf <= installment.amount

        paid_date = invoices_data[f'{index}_paid_date']

        Invoice.objects.create(project=project,
                               installment=installment,
                               amount=amount_chf,
                               received_date=received_date,
                               sent_for_payment_date=invoices_data[f'{index}_sent_for_payment'],
                               paid_date=invoices_data[f'{index}_paid_date'],
                               file=file
                               )

        comments.append(f'Invoice paid on {format_date(paid_date)} with amount {thousands_separator(amount_chf)} CHF ' \
                        f'was of {thousands_separator(amount_eur)} EUR')

        index += 1

    comment_text = '\n\n'.join(comments)

    assert project.projectcomment_set.all().count() == 1

    comment = project.projectcomment_set.all()[0]

    comment.text += comment_text
    comment.save()


def validate_project(project):
    pass
    # assert that total paid amount is not bigger than the allocated amount for the project
    # Something else?


def set_reports(project, reports_data, report_model):
    index = 1

    while f'{index}_received_date' in reports_data:
        received_date = reports_data[f'{index}_received_date']

        if received_date is None:
            break

        approved_by = create_or_get_physical_person(reports_data[f'{index}_approved_by__first_name'],
                                                    reports_data[f'{index}_approved_by__surname'])

        file = create_simple_uploaded_file(reports_data[f'{index}_file'])

        report_model.objects.create(project=project,
                                    file=file,
                                    received_date=received_date,
                                    sent_for_approval_date=reports_data[f'{index}_sent_for_approval_date'],
                                    approval_date=reports_data[f'{index}_approval_date'],
                                    approved_by=approved_by)

        index += 1


def set_financial_reports(project, financial_reports_data):
    set_reports(project, financial_reports_data, FinancialReport)


def set_scientific_reports(project, scientific_reports_data):
    set_reports(project, scientific_reports_data, ScientificReport)


def replace_if_needed(project_data, field_name, value):
    PLACEHOLDERS = ('Pending question to Laurence', 'Pending from Laurence',)

    if project_data[field_name] in PLACEHOLDERS:
        project_data[field_name] = value

    return project_data


def set_fake_data(project_data):
    replace_if_needed(project_data, 'start_date', '01-07-2016')
    replace_if_needed(project_data, 'end_date', '01-07-2021')
    replace_if_needed(project_data, 'allocated_budget_chf', 250_000)

    replace_if_needed(project_data, 'closed_date', '01-08-2021')
    replace_if_needed(project_data, 'closed_by__first_name', 'Laurence')
    replace_if_needed(project_data, 'closed_by__surname', 'Mottaz')

    replace_if_needed(project_data, 'installment_1_amount_chf', 100_000)
    replace_if_needed(project_data, 'installment_2_amount_chf', 100_000)
    replace_if_needed(project_data, 'installment_3_amount_chf', 50_000)

    replace_if_needed(project_data, 'invoice_1_received_date', '01-10-2016')
    replace_if_needed(project_data, 'invoice_1_sent_for_payment', '15-10-2016')
    replace_if_needed(project_data, 'invoice_1_paid_date', '01-12-2016')
    replace_if_needed(project_data, 'invoice_1_amount_eur', 12_000)
    replace_if_needed(project_data, 'invoice_1_amount_chf', 100_000)
    replace_if_needed(project_data, 'invoice_1_file', None)

    replace_if_needed(project_data, 'invoice_2_amount_chf', 100_000)
    replace_if_needed(project_data, 'invoice_2_amount_eur', 13_000)
    replace_if_needed(project_data, 'invoice_2_file', None)
    replace_if_needed(project_data, 'invoice_2_received_date', '01-10-2016')

    replace_if_needed(project_data, 'invoice_3_amount_chf', 50_000)
    replace_if_needed(project_data, 'invoice_3_file', None)
    replace_if_needed(project_data, 'invoice_3_received_date', '01-07-2017')

    project_data['keywords'] = ''

    return project_data


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
            project_data = set_fake_data(project_data)

            project_data = dictionary_strings_to_types(project_data)

            principal_investigator_data = filter_dictionary(project_data, 'principal_investigator__')
            principal_investigator = create_or_get_person_position(principal_investigator_data)

            project = create_project(project_data, principal_investigator)

            set_geographical_areas(project, project_data['geographical_areas'])
            set_keywords(project, project_data['keywords'])

            grant_agreement_data = filter_dictionary(project_data, 'grant_agreement__')
            set_grant_agreement(project, grant_agreement_data)

            installments_data = filter_dictionary(project_data, 'installment_')
            set_installments(project, installments_data)

            invoices_data = filter_dictionary(project_data, 'invoice_')
            set_invoices(project, invoices_data)

            financial_reports_data = filter_dictionary(project_data, 'financial_report_')
            set_financial_reports(project, financial_reports_data)

            scientific_reports_data = filter_dictionary(project_data, 'scientific_report_')
            set_scientific_reports(project, scientific_reports_data)

            validate_project(project)

            # At the moment importing only one
            break


# TODO: It might be needed to add the possibility of:
# -Add a comment for missing invoices? (e.g. where they were, why they are not available)
# -Add a comment that all the scientific reports were also reviewed by X person
# -Add a comment that all the financial reports were also reviewed by Y person
# -We've added some new fields in the CSV:
#   -attachment_N_category/file/text and f
#   -financial_report_N_comment


# Delete a project with some of the dependents:
"""
from grant_management.models import Invoice, Installment, GrantAgreement
from project_core.models import Project

project_id = 187

project = Project.objects.get(id=project_id)

project.grantagreement.delete()
project.invoice_set.all().delete()
project.installment_set.all().delete()
project.financialreport_set.all().delete()
project.scientificreport_set.all().delete()
project.projectcomment_set.all().delete()
 
project.delete()
"""
