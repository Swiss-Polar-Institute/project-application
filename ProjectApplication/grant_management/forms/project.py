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

        is_standalone_project = self.instance.id is None \
                                or self.instance.call is None

        if self.instance.id:
            submit_text = 'Save Project'
            cancel_url = reverse('logged-project-detail', kwargs={'pk': self.instance.id})
        else:
            submit_text = 'Create Project'
            cancel_url = reverse('logged-project-list')

        if is_standalone_project:
            self.fields['funding_instrument'].queryset = FundingInstrument.objects.order_by('long_name')
            self.fields['geographical_areas'].required = False

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
            funding_instrument_div = None
            finance_year_div = None
            allocated_budget_div = None


        self.helper.layout = Layout(
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),
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
                Div(HTML('Please contact an administrator to enter new locations with latitudes and longitudes'),
                    css_class='col-12'),
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
            project.key = 'Test 03'

        return super().save(**kwargs)


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
        fields = ['title', 'funding_instrument', 'finance_year', 'keywords', 'geographical_areas',
                  'location', 'start_date', 'end_date', 'allocated_budget']
        labels = {'location': 'Precise region'}
        widgets = {'start_date': XDSoftYearMonthDayPickerInput,
                   'end_date': XDSoftYearMonthDayPickerInput,
                   'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keywords'),
                   'geographical_areas': forms.CheckboxSelectMultiple,
                   }
