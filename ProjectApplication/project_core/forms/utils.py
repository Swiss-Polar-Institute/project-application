from crispy_forms.layout import HTML
from dal import autocomplete
from django import forms
from django.forms import ModelChoiceField, ModelMultipleChoiceField

from ..models import OrganisationName, PhysicalPerson, PersonPosition


def create_person_position(orcid, first_name, surname, gender=None, phd_date=None,
                           academic_title=None, group=None, career_stage=None, organisation_names=None):
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
        person_position.organisation_names.set(organisation_names)
        person_position.save()

    assert person_position

    return person_position


def get_model_information(model, field, information):
    return getattr(model._meta.get_field(field), information)


def get_field_information(model, field, label=None, help_text=None):
    kwargs = {}

    kwargs['help_text'] = get_model_information(model, field, 'help_text')
    kwargs['required'] = not get_model_information(model, field, 'blank')
    max_length = get_model_information(model, field, 'max_length')
    kwargs['validators'] = get_model_information(model, field, 'validators')

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
                                               help_text=help_text + ' If they are not available type the name and click on "Create".',
                                               label='Organisation(s)', )


def cancel_edit_button(url):
    return HTML(f'<a class="btn btn-danger" href="{url}">Cancel Edit</a>')
