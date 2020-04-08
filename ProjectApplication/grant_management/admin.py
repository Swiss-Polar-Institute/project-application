from django.contrib import admin

from .models import (GrantAgreement, Invoice, FinanceReport, LaySummary, License, Media, ProjectSocialMedia,
                     Publication, Dataset)


class GrantAgreementAdmin(admin.ModelAdmin):
    list_display = ('project', 'signed_date', 'signed_by', 'file')
    fields = ['project', ('signed_date', 'signed_by'), 'file']


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'sent_date', 'reception_date', 'due_date', 'paid_date', 'file')
    fields = ['project', 'amount', 'sent_date', 'reception_date', 'due_date', 'paid_date', 'file']


class FinanceReportAdmin(admin.ModelAdmin):
    list_display = ('sent_for_approval_date', 'signed_by', 'file')
    fields = ['sent_for_approval_date', 'signed_by', 'file']


class LaySummaryAdmin(admin.ModelAdmin):
    list_display = ('project', 'text', 'author', 'web_version', 'due_date', 'sent_date', 'reception_date')
    fields = ['project', 'text', 'author', 'web_version', 'due_date', 'sent_date', 'reception_date']


class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'public_text')
    fields = ['name', 'public_text']


class MediaAdmin(admin.ModelAdmin):
    list_display = ('author', 'license', 'copyright', 'project', 'due_date', 'sent_date', 'reception_date')
    fields = ['author', 'license', 'copyright', 'project', 'due_date', 'sent_date', 'reception_date']


class ProjectSocialMediaAdmin(admin.ModelAdmin):
    list_display = ('project', 'social_network', 'url')
    fields = ['project', 'social_network', 'url']


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'reference', 'title', 'date_time_published')
    fields = ['project', 'doi', 'reference', 'title', 'date_time_published']


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'url', 'title', 'date_published')
    fields = ['project', 'doi', 'url', 'title', 'date_published']


# Register your models here.
admin.site.register(GrantAgreement, GrantAgreementAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(FinanceReport, FinanceReportAdmin)
admin.site.register(LaySummary, LaySummaryAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(ProjectSocialMedia, ProjectSocialMediaAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Dataset, DatasetAdmin)
