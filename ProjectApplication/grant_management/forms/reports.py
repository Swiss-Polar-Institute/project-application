from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.forms.abstract_reports import AbstractReportItemModelForm
from grant_management.forms.valid_if_empty import ValidIfEmpty
from grant_management.models import ScientificReport, FinancialReport
from project_core.models import Project


class ReportItemModelForm(AbstractReportItemModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._valid_if_empty = ValidIfEmpty(fields_allowed_empty=['due_date'],
                                            basic_fields=AbstractReportItemModelForm.BASIC_FIELDS,
                                            form=self)

        self._valid_if_empty.update_required(self.fields)

    def save(self, *args, **kwargs):
        return self._valid_if_empty.save(*args, **kwargs)

    def is_valid(self):
        valid = super(__class__, self).is_valid()
        return valid or self._valid_if_empty._is_empty()
        # return self._valid_if_empty.is_valid()

    class Meta(AbstractReportItemModelForm.Meta):
        pass


class FinancialReportItemModelForm(ReportItemModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(ReportItemModelForm.Meta):
        model = FinancialReport


class ScientificReportItemModelForm(ReportItemModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(ReportItemModelForm.Meta):
        model = ScientificReport


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
