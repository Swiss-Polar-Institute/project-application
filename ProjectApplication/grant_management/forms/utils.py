from project_core.utils.utils import format_date


def error_due_date_too_early(project_start_date):
    return f'Due date should be after project start date ({format_date(project_start_date)})'


def error_due_date_too_late(project_end_date):
    return f'Due date should be before the project end date ({format_date(project_end_date)})'


def error_received_date_too_early(project_start_date):
    return f'Date received should be after project start date ({format_date(project_start_date)})'
