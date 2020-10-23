from django.contrib import admin

from reporting.models import FundingInstrumentYearMissingData


class FundingInstrumentYearMissingDataAdmin(admin.ModelAdmin):
    list_display = ('funding_instrument', 'finance_year')
    ordering = ['funding_instrument', 'finance_year', ]


admin.site.register(FundingInstrumentYearMissingData, FundingInstrumentYearMissingDataAdmin)
