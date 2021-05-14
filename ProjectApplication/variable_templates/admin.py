from django.contrib import admin

import variable_templates.models


class TemplateVariableNameAdmin(admin.ModelAdmin):
    search_fields = ('name', 'default', 'description', )
    list_display = ('name', 'default', 'description', )
    ordering = ('name', 'default', 'description', )


class FundingInstrumentVariableTemplateAdmin(admin.ModelAdmin):
    search_fields = ('funding_instrument__long_name', 'name__name', 'value', )
    list_display = ('funding_instrument', 'name', 'value', )
    ordering = ('name', 'value', )


class CallVariableTemplateAdmin(admin.ModelAdmin):
    search_fields = ('call__long_name', 'name__name', 'value', )
    list_display = ('call', 'name', 'value', )
    ordering = ('name', 'value', )


admin.site.register(variable_templates.models.TemplateVariableName, TemplateVariableNameAdmin)
admin.site.register(variable_templates.models.FundingInstrumentVariableTemplate, FundingInstrumentVariableTemplateAdmin)
admin.site.register(variable_templates.models.CallVariableTemplate, CallVariableTemplateAdmin)
