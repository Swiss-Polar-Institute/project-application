from django.core.exceptions import ObjectDoesNotExist



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
