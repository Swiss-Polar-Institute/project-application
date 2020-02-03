import subprocess

from django import template

register = template.Library()


@register.simple_tag
def version_date():
    try:
        date_time = subprocess.run(['/usr/bin/git', 'log', '-1', '--format=%cd'], capture_output=True).stdout
        return date_time.decode('utf-8').strip()
    except FileNotFoundError:
        return 'Unknown'

