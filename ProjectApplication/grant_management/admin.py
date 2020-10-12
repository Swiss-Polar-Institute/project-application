from django.contrib import admin

from .models import (GrantAgreement, Invoice, FinancialReport, LaySummary, License, Medium, MediumDeleted,
                     ProjectSocialNetwork, Publication, Dataset, LaySummaryType, BlogPost, SocialNetwork, Installment)


class GrantAgreementAdmin(admin.ModelAdmin):
    list_display = ('project', 'signed_date', 'signed_by_list', 'file')

    def signed_by_list(self, obj):
        if obj.signed_by.exists():
            result = ''
            for physical_person in obj.signed_by.all():
                if result != '':
                    result += ', '
                result += str(physical_person)
        else:
            result = '-'

        return result


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'sent_for_payment_date', 'received_date', 'due_date', 'paid_date',
                    'allow_overbudget', 'overbudget_allowed_by', 'file')


class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('project', 'approval_date', 'approved_by', 'file')


class LaySummaryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class LaySummaryAdmin(admin.ModelAdmin):
    list_display = ('project', 'text', 'author', 'lay_summary_type', 'due_date', 'received_date')


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('project', 'text', 'author', 'due_date', 'received_date')


class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'public_text')


class MediumAdmin(admin.ModelAdmin):
    list_display = ('photographer', 'license', 'copyright', 'project', 'file_md5', 'created_on', 'modified_on',)


class MediumDeletedAdmin(admin.ModelAdmin):
    list_display = ('photographer', 'license', 'copyright', 'project', 'file_md5', 'created_on', 'modified_on',)


class ProjectSocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('project', 'social_network', 'url')


class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('name',)


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'reference', 'title', 'published_date')


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('project', 'doi', 'url', 'title', 'published_date')


class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount')


admin.site.register(GrantAgreement, GrantAgreementAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(FinancialReport, FinancialReportAdmin)
admin.site.register(LaySummaryType, LaySummaryTypeAdmin)
admin.site.register(LaySummary, LaySummaryAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Medium, MediumAdmin)
admin.site.register(MediumDeleted, MediumDeletedAdmin)
admin.site.register(ProjectSocialNetwork, ProjectSocialNetworkAdmin)
admin.site.register(SocialNetwork, SocialNetworkAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Installment, InstallmentAdmin)
