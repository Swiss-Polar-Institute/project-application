from django.contrib import admin

from reporting.models import FundingInstrumentYearMissingData


class FundingInstrumentYearMissingDataAdmin(admin.ModelAdmin):
    search_fields = ('funding_instrument__long_name', 'finance_year', 'missing_data_type', 'description', )

    list_display = ('funding_instrument', 'finance_year', 'missing_data_type', 'description',)
    ordering = ('funding_instrument', 'finance_year', 'missing_data_type', 'description',)


admin.site.register(FundingInstrumentYearMissingData, FundingInstrumentYearMissingDataAdmin)
