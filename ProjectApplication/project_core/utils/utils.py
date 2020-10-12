import hashlib
import io

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import FileExtensionValidator


def bytes_to_human_readable(num: int) -> str:
    if num is None:
        return 'Unknown'

    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if abs(num) < 1024.0:
            if unit == 'bytes':
                return '{} {}'.format(num, unit)
            else:
                return '{:.2f} {}'.format(num, unit)
        num /= 1024.0
    return '%d %s' % (num, 'YB')


def user_is_in_group_name(user, group_name):
    try:
        user.groups.get(name=group_name)
        return True
    except ObjectDoesNotExist:
        return False


def create_person_position(orcid, first_name, surname, gender=None, phd_date=None,
                           academic_title=None, group=None, career_stage=None, organisation_names=None):
    from ..models import PhysicalPerson, PersonPosition

    """
    Creates a PhysicalPerson (if needed) and a PersonPosition. Returns the PersonPosition.
    """
    physical_person, physical_person_created = PhysicalPerson.objects.get_or_create(orcid=orcid)

    # Updates any previous information (besides the ORCID that it stays the same or it's creating a new person)
    physical_person.first_name = first_name
    physical_person.surname = surname

    if gender:
        physical_person.gender = gender

    if phd_date:
        physical_person.phd_date = phd_date

    physical_person.save()

    person_position_filter = {'person': physical_person,
                              'academic_title': academic_title}

    if career_stage:
        person_position_filter['career_stage'] = career_stage

    if group:
        person_position_filter['group'] = group

    person_positions = PersonPosition.objects.filter(**person_position_filter)

    person_position_found = False
    person_position = None

    for person_position in person_positions:
        if set(person_position.organisation_names.all()) == set(organisation_names):
            person_position_found = True
            break

    if not person_position_found:
        person_position = PersonPosition.objects.create(person=physical_person,
                                                        academic_title=academic_title,
                                                        group=group,
                                                        career_stage=career_stage)
        if organisation_names:
            person_position.organisation_names.set(organisation_names)

    assert person_position

    person_position.save()

    return person_position


def format_date(date):
    return f'{date:%d-%m-%Y}'


def file_size_validator(file):
    file_size = file.file.size
    limit = 150 * 1024 * 1024

    if file_size > limit:
        raise ValidationError(f'Maximum file size is {bytes_to_human_readable(limit)}')


def management_file_validator():
    return [FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'jpeg', 'png']),
            file_size_validator]


def external_file_validator():
    return [FileExtensionValidator(allowed_extensions=['pdf']),
            file_size_validator]


def calculate_md5_from_file_field(file_field):
    # initial_position = file_field.file.file.pos()
    # file_field.file.file.seek(0)

    if type(file_field.file.file) == io.BytesIO:
        file_contents = file_field.file.file.getvalue()
    else:
        # This is horrible. It happens when the file is updated
        # (at least in our flow)
        file_contents = file_field.file.read()

    hash_md5 = hashlib.md5(file_contents)

    # file_field.file.file.seek(initial_position)

    return hash_md5.hexdigest()

