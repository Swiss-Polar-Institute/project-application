from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.forms.abstract_reports import AbstractReportItemModelForm
from grant_management.models import ScientificReport, FinancialReport
from project_core.models import Project


class FinancialReportItemModelForm(AbstractReportItemModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cd = super().clean()

        project = cd['project']

        if project.is_active() is False:
            raise ValidationError(f'Cannot modify financial reports for this project: the status is {project.status}')

    class Meta(AbstractReportItemModelForm.Meta):
        model = FinancialReport


class ScientificReportItemModelForm(AbstractReportItemModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cd = super().clean()

        project = cd['project']

        if project.is_active() is False:
            raise ValidationError(f'Cannot modify scientific reports for this project: the status is {project.status}')

    class Meta(AbstractReportItemModelForm.Meta):
        model = ScientificReport


class ReportsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('due_date')


ScientificReportsInlineFormSet = inlineformset_factory(Project, ScientificReport,
                                                       form=ScientificReportItemModelForm,
                                                       formset=ReportsFormSet,
                                                       min_num=1, extra=0, can_delete=True)

FinancialReportsInlineFormSet = inlineformset_factory(Project, FinancialReport,
                                                      form=FinancialReportItemModelForm,
                                                      formset=ReportsFormSet,
                                                      min_num=1, extra=0, can_delete=True)
