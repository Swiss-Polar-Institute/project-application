from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from dal import autocomplete
from django import forms
from django.urls import reverse

from grant_management.forms import utils
from project_core.widgets import XDSoftYearMonthDayPickerInput


class AbstractReportItemModelForm(forms.ModelForm):
    BASIC_FIELDS = ['project', 'id', 'DELETE', 'can_be_deleted']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        final_fields = ['approved_by', 'approval_date']

        for field_name, field in self.fields.items():
            if type(field) == forms.DateField:
                XDSoftYearMonthDayPickerInput.set_format_to_field(field)

        self.fields['can_be_deleted'] = forms.CharField(initial=1, required=False)

        new_person_url = reverse('logged-person-position-add')
        self.fields['approved_by'].help_text += f' . You can <a href="{new_person_url}">add a new person</a> if needed'

        message = ''
        # Final fields are all or none - it checks for the first one
        if self.instance and getattr(self.instance, final_fields[0]) is not None:
            message = '''<strong>This report has been signed and can no longer be changed. 
            To edit any of the fields, delete the signed by and date signed, 
            click on <em>Save Financial Reports</em> and come back again.</strong>'''
            self.fields['can_be_deleted'].initial = 0
            for field_name in self.fields:
                if field_name not in AbstractReportItemModelForm.BASIC_FIELDS and field_name not in final_fields:
                    self.fields[field_name].disabled = True

        self.helper = FormHelper()
        self.helper.form_tag = False

        # It's included in the main formset, it avoids problems when adding new invoices and the jquery.formset.js
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                Div('can_be_deleted', hidden=True, css_class='can_be_deleted'),
                css_class='row', hidden=True
            ),
            Div(
                Div(
                    HTML(message), css_class='col-12'),
                css_class='row to-delete'
            ),
            Div(
                Div('due_date', css_class='col-4'),
                Div('received_date', css_class='col-4'),
                Div('file', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('sent_for_approval_date', css_class='col-4'),
                Div('approved_by', css_class='col-4'),
                Div('approval_date', css_class='col-4'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        if self.errors:
            return cd

        project = cd['project']
        project_starts = project.start_date
        project_ends = project.end_date

        due_date = cd.get('due_date', None)
        received_date = cd.get('received_date', None)
        sent_for_approval_date = cd.get('sent_for_approval_date', None)
        approval_date = cd.get('approval_date', None)
        approved_by = cd.get('approved_by', None)
        file = cd.get('file', None)

        errors = {}

        if due_date and due_date < project_starts:
            errors['due_date'] = utils.error_due_date_too_early(project)

        if due_date and due_date > project_ends:
            errors['due_date'] = utils.error_due_date_too_late(project)

        if received_date and received_date < project_starts:
            errors['received_date'] = utils.error_received_date_too_early(project)

        if sent_for_approval_date and received_date and sent_for_approval_date < received_date:
            errors['sent_for_approval_date'] = 'Date sent for approval should be after the date the report was received'

        if approval_date and sent_for_approval_date and approval_date < sent_for_approval_date:
            errors['approval_date'] = 'Date the report was approved should be after the date it was sent for approval.'

        if not approved_by and approval_date:
            errors['approved_by'] = 'Please enter who approved the report (the approval date has been entered).'

        if not file and received_date:
            errors['file'] = 'Please attach the report file (the date received has been entered).'

        if not received_date and sent_for_approval_date:
            errors['received_date'] = 'Please enter the date the report was received (the date it was ' \
                                      'sent for approval has been entered).'

        if not sent_for_approval_date and approval_date:
            errors['sent_for_approval_date'] = 'Please enter the date the report was sent for approval (the date it ' \
                                               'was approved has been entered).'

        if not approval_date and approved_by:
            errors['approval_date'] = 'Please enter the date the report was approved (the person who ' \
                                      'approved it has been entered).'

        if errors:
            raise forms.ValidationError(errors)

        return cd

    def is_valid(self):
        return super().is_valid()

    class Meta:
        # model = XXX  # : this needs to be defined by the subclass
        fields = ['project', 'due_date', 'received_date', 'sent_for_approval_date', 'approval_date', 'approved_by',
                  'file']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'received_date': XDSoftYearMonthDayPickerInput,
            'sent_for_approval_date': XDSoftYearMonthDayPickerInput,
            'approval_date': XDSoftYearMonthDayPickerInput,
            'approved_by': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')
        }
        labels = {'due_date': 'Due',
                  'received_date': 'Received',
                  'sent_for_approval_date': 'Sent for approval',
                  }
        help_texts = {'due_date': 'Date the report is due', 'received_date': 'Date the report was received'}
