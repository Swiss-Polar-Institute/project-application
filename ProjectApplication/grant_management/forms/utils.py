from project_core.utils.utils import format_date


def error_due_date_too_early(project):
    return f'Due date should be after project start date ({format_date(project.start_date)})'


def error_due_date_too_late(project):
    return f'Due date should be before the project end date ({format_date(project.end_date)})'


def error_received_date_too_early(project):
    return f'Date received should be after project start date ({format_date(project.start_date)})'
