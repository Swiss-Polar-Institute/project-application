from django.urls import reverse
from django.utils.safestring import mark_safe

from project_core.utils.utils import format_date


def error_due_date_too_early(project):
    project_basic_information_edit = reverse('logged-grant_management-project-basic-information-update',
                                             kwargs={'project': project.id})

    return mark_safe(f'Due date should be after project start date ({format_date(project.start_date)})'
                     f'If needed <a href="{project_basic_information_edit}">edit the project start date</a>.')


def error_due_date_too_late(project):
    project_basic_information_edit = reverse('logged-grant_management-project-basic-information-update',
                                             kwargs={'project': project.id})
    return mark_safe(
        f'Due date should be before the project end date ({format_date(project.end_date)}). '
        f'If needed <a href="{project_basic_information_edit}">edit the project end date</a>.')


def error_received_date_too_early(project):
    project_basic_information_edit = reverse('logged-grant_management-project-basic-information-update',
                                             kwargs={'project': project.id})

    return mark_safe(f'Date received should be after project start date ({format_date(project.start_date)})'
                     f'If needed <a href="{project_basic_information_edit}">edit the project start date</a>.')
