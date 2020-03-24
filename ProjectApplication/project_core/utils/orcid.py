from crispy_forms.bootstrap import AppendedText
from crispy_forms.layout import Div
from django.utils.safestring import mark_safe


def orcid_div():
    return Div(
        Div(AppendedText('orcid', mark_safe('<i class="fab fa-orcid" style="color:#a6ce39"></i>')),
            css_class='col-8'),
        css_class='row'
    )


def field_set_read_only(fields):
    # Only use this function if disabled=True cannot be used
    # (disabled=True makes Django not add the field in self.cleaned_data,
    # in ORCID iD context we want the read only fields in the self.cleaned_data at the moment

    for field in fields:
        field.widget.attrs.update({'readonly': 'readonly'})
