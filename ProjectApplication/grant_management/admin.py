from django.contrib import admin

from .models import (GrantAgreement, Invoice, FinanceReport, LaySummary, License, Media, ProjectSocialMedia,
                     Publication, Dataset)


class GrantAdmin(admin.ModelAdmin):
    list_display = ('project', 'signed_date', 'signed_by', 'file')
    fields = ['project', 'signed_date', 'signed_by', 'file']


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'sent_date', 'reception_date', 'due_date', 'paid_date', 'urls', 'file')
    fields = ['project', 'amount', 'sent_date', 'reception_date', 'due_date', 'paid_date', 'urls', 'file']


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
    list_display = ('project', 'doi', 'reference', 'title', 'date_published')
    fields = ['project', 'doi', 'reference', 'title', 'date_published']


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'url', 'title', 'date_published')
    fields = ['project', 'doi', 'url', 'title', 'date_published']


# Register your models here.
admin.site.register(GrantAgreement)
admin.site.register(Invoice)
admin.site.register(FinanceReport)
admin.site.register(LaySummary)
admin.site.register(License)
admin.site.register(Media)
admin.site.register(ProjectSocialMedia)
admin.site.register(Publication)
admin.site.register(Dataset)
