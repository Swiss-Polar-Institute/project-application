from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, HTML, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError

from project_core.models import Project


class CloseProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].choices.remove(('Ongoing', 'Ongoing'))
        self.fields['status'].widget.choices.remove(('Ongoing', 'Ongoing'))
        self.fields['status'].initial = None

        self.fields['abortion_reason'].help_text = 'Mandatory if the Status is "Aborted"'

        # Using Javascript it makes it optional if the status is completed
        self.fields['abortion_reason'].label = 'Abortion reason<span class="asteriskField">*</span>'

        self.helper = FormHelper()

        divs = [
            Div(
                Div(HTML('{% include "grant_management/_close_project-invoice_summary.tmpl" %}'),
                    css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('{% include "grant_management/_close_project-financial_reports.tmpl" %}'),
                    css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('<h4>Milestones</h4>To do'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('{% include "grant_management/_close_project-scientific_reports.tmpl" %}'),
                    css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('{% include "grant_management/_close_project-lay_summaries.tmpl" %}'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('{% include "grant_management/_close_project-blog_posts.tmpl" %}'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('<p></p>'), css_class='col-12'),
                css_class='row'
            ),
        ]

        if self._can_be_closed():
            divs += [
                Div(
                    Div('status', css_class='col-3'),
                    css_class='row'
                ),
                Div(
                    Div('abortion_reason', css_class='col-12'),
                    css_class='row'
                ),
                Div(Div(HTML(
                    '<b>After closing a project: it is not possible anymore to change installments, invoices, '
                    'financial or scientific reports</b>'),
                    css_class='col-12'), css_class='row'),
                Submit(name='close', value='Close')
            ]
        else:
            divs.append(HTML('The project cannot be closed - fix things and try again'))

        self.helper.layout = Layout(*divs)

    def _can_be_closed(self):
        return self.unpaid_invoices_count() == 0 and self.unsigned_financial_reports_count() == 0 and \
               self.unsigned_scientific_reports_count() == 0 and self.unreceived_blog_posts_count() == 0

    def empty_lay_summaries_count(self):
        return self.instance.laysummary_set.filter(text='').count()

    def unpaid_invoices_count(self):
        return self.instance.invoice_set.filter(paid_date__isnull=True).count()

    def unsigned_financial_reports_count(self):
        return self.instance.financialreport_set.filter(approval_date__isnull=True).count()

    def unsigned_scientific_reports_count(self):
        return self.instance.financialreport_set.filter(approval_date__isnull=True).count()

    def unreceived_blog_posts_count(self):
        return self.instance.blogpost_set.filter(text='').count()

    def clean(self):
        cd = super().clean()

        errors = {}

        if 'status' in cd and cd['status'] == Project.ABORTED and not cd['abortion_reason']:
            errors['abortion_reason'] = 'Abortion error is mandatory if the project is aborted'

        if errors:
            raise ValidationError(errors)

        return cd

    def save(self, commit=True):
        if self._can_be_closed():
            super().save(commit=commit)

    class Meta:
        model = Project
        fields = ['status', 'abortion_reason']
        widgets = {'status': forms.RadioSelect}
