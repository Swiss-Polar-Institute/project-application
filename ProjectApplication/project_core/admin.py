from django.contrib import admin
import project_core.models


# Register your models here.


class StepAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ['name', 'description']


class StepDateAdmin(admin.ModelAdmin):
    list_display = ()
    ordering = ['step', 'date']


admin.site.register(project_core.models.Step, StepAdmin)
admin.site.register(project_core.models.StepDate, StepDateAdmin)