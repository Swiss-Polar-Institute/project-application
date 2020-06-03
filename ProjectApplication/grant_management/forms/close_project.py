from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML
from django import forms


class CloseProjectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._project = kwargs.pop('project')

        super().__init__(*args, **kwargs)

        self.fields['project'] = forms.CharField(initial=1, required=False)
        self.fields['reason'] = forms.CharField(required=False, help_text='Reason that the project is finished')

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Div(
                Div(HTML('{% include "grant_management/_close_project-invoice_summary.tmpl" %}'), css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div(HTML('{% include "grant_management/_close_project-financial_reports.tmpl" %}'), css_class='col-12'),
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
                Div('reason', css_class='col-4'),
                css_class='row'
            )
        )

    def can_be_closed(self):
        return self.unpaid_invoices_count() == 0 and self.unsigned_financial_reports_count() == 0 and \
               self.unsigned_scientific_reports_count() == 0

    def empty_lay_summaries_count(self):
        return self._project.laysummary_set.filter(text='').count()

    def unpaid_invoices_count(self):
        return self._project.invoice_set.filter(paid_date__isnull=True).count()

    def unsigned_financial_reports_count(self):
        return self._project.financialreport_set.filter(approval_date__isnull=True).count()

    def unsigned_scientific_reports_count(self):
        return self._project.financialreport_set.filter(approval_date__isnull=True).count()

    def unreceived_blog_posts_count(self):
        return self._project.blogpost_set.filter(text='').count()

    def clean(self):
        cd = super().clean()
        return cd
