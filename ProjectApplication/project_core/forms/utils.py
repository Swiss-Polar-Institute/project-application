from dal import autocomplete
from django import forms
from django.forms import ModelChoiceField, ModelMultipleChoiceField

from ..models import OrganisationName


def get_model_information(model, field, information):
    return getattr(model._meta.get_field(field), information)


def get_field_information(model, field, label=None, help_text=None):
    kwargs = {}

    kwargs['help_text'] = get_model_information(model, field, 'help_text')
    kwargs['required'] = not get_model_information(model, field, 'blank')

    max_length = get_model_information(model, field, 'max_length')
    if max_length is not None:
        kwargs['max_length'] = max_length

    if label is not None:
        kwargs['label'] = label

    if help_text is not None:
        kwargs['help_text'] = help_text

    return kwargs


class PlainTextWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            if type(value) == str:
                final_value = value
            else:
                final_value = value.id

            return '<input type="hidden" name="{}" value="{}" id="{}">'.format(name, final_value, attrs['id'])
        else:
            return '-'


class LabelAndOrderNameChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = kwargs['queryset'].order_by('name')
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class OrganisationNameChoiceField(ModelChoiceField):
    def label_from_instance(self, organisation):
        return organisation.name


class OrganisationNameMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, organisation_name):
        return organisation_name.name


def organisations_name_autocomplete(initial, help_text):
    return OrganisationNameMultipleChoiceField(queryset=OrganisationName.objects.all(),
                                               widget=autocomplete.ModelSelect2Multiple(
                                                   url='autocomplete-organisation-names'),
                                               initial=initial,
                                               help_text=help_text + ' If it is not available type the name and click on "Create"',
                                               label='Organisation(s)', )
