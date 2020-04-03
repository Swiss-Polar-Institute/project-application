from django.contrib import admin

from .models import (GrantAgreement)

# Register your models here.
admin.site.register(GrantAgreement)


class GrantAdmin(admin.ModelAdmin):
    list_display = ('project', 'signed_date', 'signed_by', 'file')
    fields = ['project', ('signed_date', 'signed_by'), 'file']
