from project_core.utils.utils import format_date


def error_due_date_too_early(project_start_date):
    return f'Due date needs to be after project start date ({format_date(project_start_date)})'


def error_due_date_too_late(project_end_date):
    return f'Due date needs to be before the project ends date ({format_date(project_end_date)})'


def error_reception_date_too_early(project_start_date):
    return f'Reception date needs to be after project start date ({format_date(project_start_date)})'
