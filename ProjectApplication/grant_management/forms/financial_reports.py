from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory, BaseInlineFormSet

from grant_management.models import FinancialReport
from project_core.models import Project
from .abstract_reports import AbstractReportItemModelForm
from .valid_if_empty import ValidIfEmpty


class FinancialReportItemModelForm(AbstractReportItemModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._valid_if_empty = ValidIfEmpty(fields_allowed_empty=['due_date'],
                                            basic_fields=AbstractReportItemModelForm.BASIC_FIELDS,
                                            form=self)

        self._valid_if_empty.update_required(self.fields)

    def save(self, *args, **kwargs):
        return self._valid_if_empty.save(*args, **kwargs)

    def is_valid(self):
        return self._valid_if_empty.is_valid()

    class Meta(AbstractReportItemModelForm.Meta):
        model = FinancialReport
