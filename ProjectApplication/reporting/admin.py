from django.contrib import admin

from reporting.models import FundingInstrumentYearMissingData


class FundingInstrumentYearMissingDataAdmin(admin.ModelAdmin):
    list_display = ('funding_instrument', 'finance_year', 'missing_data_type', 'description',)
    ordering = ('funding_instrument', 'finance_year', 'missing_data_type', 'description',)


admin.site.register(FundingInstrumentYearMissingData, FundingInstrumentYearMissingDataAdmin)
