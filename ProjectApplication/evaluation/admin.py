from django.contrib import admin

from .models import Reviewer


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'calls_list')
    filter_horizontal = ('calls',)


    def calls_list(self, obj):
        return ', '.join([str(call) for call in obj.calls.all()])


admin.site.register(Reviewer, ReviewerAdmin)
