from crispy_forms.bootstrap import AppendedText
from crispy_forms.layout import Div
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe


def orcid_div(field_name):
    return Div(
        Div(AppendedText(field_name, mark_safe('<i class="fab fa-orcid" style="color:#a6ce39"></i>')),
            css_class='col-8'),
        css_class='row'
    )


def field_set_read_only(fields):
    # Only use this function if disabled=True cannot be used
    # (disabled=True makes Django not add the field in self.cleaned_data,
    # in ORCID iD context we want the read only fields in the self.cleaned_data at the moment

    for field in fields:
        field.widget.attrs.update({'readonly': 'readonly'})


def raise_error_if_orcid_invalid(orcid):
    if orcid == '0000-0002-1825-0097':
        raise ValidationError('0000-0002-1825-0097 is the example ORCID and cannot be used')


def orcid_validators():
    return [raise_error_if_orcid_invalid,
            RegexValidator(regex='^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$',
                           message='Invalid format for ORCID iD. E.g.: 0000-0002-1825-0097.',
                           code='Invalid format')
            ]
