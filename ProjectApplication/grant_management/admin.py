from django.contrib import admin

from .models import (GrantAgreement, Invoice, FinancialReport, LaySummary, License, Media, ProjectSocialMedia,
                     Publication, Dataset)


class GrantAgreementAdmin(admin.ModelAdmin):
    list_display = ('project', 'signed_date', 'signed_by', 'file')


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'sent_date', 'reception_date', 'due_date', 'paid_date', 'file')


class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('project', 'approval_date', 'approved_by', 'file')


class LaySummaryAdmin(admin.ModelAdmin):
    list_display = ('project', 'text', 'author', 'web_version', 'due_date', 'sent_date', 'reception_date')


class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'public_text')


class MediaAdmin(admin.ModelAdmin):
    list_display = ('author', 'license', 'copyright', 'project', 'due_date', 'sent_date', 'reception_date')


class ProjectSocialMediaAdmin(admin.ModelAdmin):
    list_display = ('project', 'social_network', 'url')


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'reference', 'title', 'date_time_published')


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'url', 'title', 'date_published')


# Register your models here.
admin.site.register(GrantAgreement, GrantAgreementAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(FinancialReport, FinancialReportAdmin)
admin.site.register(LaySummary, LaySummaryAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(ProjectSocialMedia, ProjectSocialMediaAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Dataset, DatasetAdmin)
