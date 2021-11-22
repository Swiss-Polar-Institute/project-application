from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML
from dal import autocomplete
from django import forms
from django.urls import reverse

from project_core.forms.utils import cancel_edit_button
from project_core.models import Project, FundingInstrument
from project_core.widgets import XDSoftYearMonthDayPickerInput


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['start_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['end_date'])

        self.helper = FormHelper(self)

        is_standalone_project = self.instance.id is None or self.instance.call is None

        if self.instance.id:
            submit_text = 'Save Project'
            cancel_url = reverse('logged-project-detail', kwargs={'pk': self.instance.id})

            grant_management_deliverables_url = reverse('logged-grant_management-project-detail',
                                                        kwargs={'pk': self.instance.id})

            locations_link = f'{grant_management_deliverables_url}?tab=other#locations'
            locations_message = f'Use the <a href="{locations_link}">"Other" tab under grant management</a> to edit the project locations.'

        else:
            submit_text = 'Create Project'
            cancel_url = reverse('logged-project-list')
            locations_message = 'Use the "Other" tab under grant management to add the project locations after creating it. '

        # Applicants need to enter 5 keywords in the proposal, SPI at the moment can create or save them without keywords
        self.fields['keywords'].required = False

        if is_standalone_project:
            self.fields['funding_instrument'].queryset = FundingInstrument.objects.order_by('long_name')
            self.fields['geographical_areas'].required = False

            principal_investigator_div = Div(
                Div('principal_investigator', css_class='col-12'),
                css_class='row'
            )

            create_person_url = reverse('logged-person-position-add')

            self.fields[
                'principal_investigator'].help_text += \
                f'. If the principal investigator is not found <a href="{create_person_url}">create</a> the person ' \
                'and try again (you need to reload the page). Only people that have accepted the privacy policy is ' \
                'displayed'

            funding_instrument_div = Div(
                Div('funding_instrument', css_class='col-12'),
                css_class='row'
            )
            finance_year_div = Div(
                Div('finance_year', css_class='col-6'),
                css_class='row'
            )
            allocated_budget_div = Div(
                Div('allocated_budget', css_class='col-6'),
                css_class='row'
            )

        else:
            principal_investigator_div = None
            funding_instrument_div = None
            finance_year_div = None
            allocated_budget_div = None

            # Used when the project is standalone (not coming from a call)
            # In Meta.fields they are added - IMHO it's easier to delete them
            # than add them here
            del self.fields['principal_investigator']
            del self.fields['finance_year']
            del self.fields['allocated_budget']
            del self.fields['funding_instrument']

        self.helper.layout = Layout(
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),
            principal_investigator_div,
            funding_instrument_div,
            finance_year_div,
            allocated_budget_div,
            Div(
                Div('keywords', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('geographical_areas', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('location', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('Locations'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML(
                    locations_message),
                    css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('<br>'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('start_date', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('end_date', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', submit_text),
                cancel_edit_button(cancel_url)
            )
        )

    def save(self, **kwargs):
        project = self.instance

        if not hasattr(project, 'principal_investigator'):
            project.principal_investigator_id = 39

        if project.key == '':
            project.key = ProjectForm._find_project_key(
                f'{project.funding_instrument.short_name}-{project.finance_year}')

        return super().save(**kwargs)

    @staticmethod
    def _find_project_key(prefix):
        counter = 1
        candidate_key = f'{prefix}-{counter:03d}'

        while Project.objects.filter(key=candidate_key).exists():
            counter += 1
            candidate_key = f'{prefix}-{counter:03d}'

        return candidate_key

    def clean(self):
        cd = super().clean()

        if self.errors:
            return cd

        errors = {}

        if 'start_date' in cd and 'end_date' in cd and \
                cd['start_date'] > cd['end_date']:
            errors['start_date'] = forms.ValidationError(
                'Start date needs to be before the end date')

        if errors:
            raise forms.ValidationError(errors)

        return cd

    class Meta:
        model = Project
        fields = ['title', 'principal_investigator', 'funding_instrument', 'finance_year', 'keywords',
                  'geographical_areas', 'location', 'start_date', 'end_date', 'allocated_budget']
        labels = {'location': 'Precise region',
                  'allocated_budget': 'Allocated budget (CHF)'
                  }
        widgets = {'principal_investigator': autocomplete.ModelSelect2(url='logged-autocomplete-person-positions'),
                   'start_date': XDSoftYearMonthDayPickerInput,
                   'end_date': XDSoftYearMonthDayPickerInput,
                   'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords'),
                   'geographical_areas': forms.CheckboxSelectMultiple,
                   }
