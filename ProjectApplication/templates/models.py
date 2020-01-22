from django.db import models

from project_core.models import CreateModify, FundingInstrument, Call


class TemplateVariableName(CreateModify):
    name = models.CharField(help_text='{{ name }} in the text where this gets replaced', max_length=200)
    default = models.CharField(help_text="Default value if a Call doesn't override it", max_length=200)
    description = models.CharField(help_text='Definition of a variable', max_length=200)

    def __str__(self):
        return f'{self.name}-{self.default}'


class AbstractVariableTemplate(CreateModify):
    name = models.ForeignKey(TemplateVariableName, blank=False, null=False, on_delete=models.PROTECT)
    value = models.CharField(help_text='Value for the variable in this funding instrument', max_length=200)

    def __str__(self):
        return f'{self.name}-{self.value}'

    class Meta:
        abstract = True


class FundingInstrumentVariableTemplate(AbstractVariableTemplate):
    funding_instrument = models.ForeignKey(FundingInstrument, help_text='Funding instrument that this text belongs to',
                                           blank=False, null=False, on_delete=models.PROTECT)

    def __str__(self):
        return f'Funding Instrument: {self.funding_instrument} - {{{self.name}}}-{self.value}'

    class Meta:
        unique_together = (('funding_instrument', 'name'),)


class CallVariableTemplate(AbstractVariableTemplate):
    call = models.ForeignKey(Call, help_text='Call that this text belongs to',
                             blank=False, null=False, on_delete=models.PROTECT)

    def __str__(self):
        return f'Funding Instrument: {self.call} - {{{self.name}}}-{self.value}'

    class Meta:
        unique_together = (('call', 'name'),)
