from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.forms.financial_reports import FinancialReportItemModelForm
from grant_management.forms.scientific_reports import ScientificReportItemModelForm
from grant_management.models import ScientificReport, FinancialReport
from project_core.models import Project


class ReportsFormSet(BaseInlineFormSet):
    FORM_NAME = 'reports_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = ReportsFormSet.FORM_NAME

    def get_queryset(self):
        return super().get_queryset().order_by('received_date')


ScientificReportsInlineFormSet = inlineformset_factory(Project, ScientificReport,
                                                       form=ScientificReportItemModelForm,
                                                       formset=ReportsFormSet,
                                                       min_num=1, extra=0, can_delete=True)

FinancialReportsInlineFormSet = inlineformset_factory(Project, FinancialReport,
                                                      form=FinancialReportItemModelForm,
                                                      formset=ReportsFormSet,
                                                      min_num=1, extra=0, can_delete=True)
