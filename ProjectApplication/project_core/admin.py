from django.contrib import admin
import project_core.models


# Register your models here.


class DateAdmin(admin.ModelAdmin):
    list_display = ('notable_date', 'date')
    ordering = ['notable_date', 'date']


class CallAdmin(admin.ModelAdmin):
    list_display = ('long_name', 'short_name', 'description', 'dates_list')
    ordering = ['long_name', 'short_name', 'description']

    def dates_list(self, obj):
        dates = obj.dates.all()

        return ", ".join(["{}".format(date) for date in dates])


admin.site.register(project_core.models.Date, DateAdmin)
admin.site.register(project_core.models.Call, CallAdmin)