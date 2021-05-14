from django.contrib import admin

from project_core.models import Project
from .models import (GrantAgreement, Invoice, FinancialReport, LaySummary, License, Medium, MediumDeleted,
                     ProjectSocialNetwork, Publication, Dataset, LaySummaryType, BlogPost, SocialNetwork, Installment)


class GrantAgreementAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('file',)
    list_display = ('project', 'signed_date', 'signed_by_list', 'file',)

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
    search_fields = Project.search_fields + ('amount', 'file',)

    list_display = ('project', 'amount', 'sent_for_payment_date', 'received_date', 'due_date', 'paid_date',
                    'allow_overbudget', 'overbudget_allowed_by', 'file',)


class FinancialReportAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('approved_by__first_name', 'approved_by__surname',
                                             'approved_by__orcid', 'file',)
    list_display = ('project', 'approval_date', 'approved_by', 'file',)


class LaySummaryTypeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description',)
    list_display = ('name', 'description',)


class LaySummaryAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('text', 'author__first_name', 'author__surname', 'lay_summary_type__name',)
    list_display = ('project', 'text', 'author', 'lay_summary_type', 'due_date', 'received_date',)


class BlogPostAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('text', 'author__first_name', 'author__surname', 'author__orcid',)
    list_display = ('project', 'text', 'author', 'due_date', 'received_date',)


class LicenseAdmin(admin.ModelAdmin):
    search_fields = ('name', 'public_text',)
    list_display = ('name', 'public_text',)


class MediumAdmin(admin.ModelAdmin):
    search_fields = ('photographer__first_name', 'photographer__surname', 'license__name',
                     'copyright') + Project.search_fields
    list_display = ('photographer', 'license', 'copyright', 'project', 'file_md5', 'created_on', 'modified_on',)


class MediumDeletedAdmin(admin.ModelAdmin):
    search_fields = ('original_id', )
    list_display = ('original_id', 'created_on', 'modified_on',)


class ProjectSocialNetworkAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('url', )
    list_display = ('project', 'social_network', 'url',)


class SocialNetworkAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name',)


class PublicationAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('doi', 'reference', 'title', )
    list_display = ('project', 'doi', 'reference', 'title', 'published_date',)


class DatasetAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('doi', 'url', 'title',)
    list_display = ('project', 'doi', 'url', 'title', 'published_date',)


class InstallmentAdmin(admin.ModelAdmin):
    search_fields = Project.search_fields + ('amount',)
    list_display = ('project', 'amount',)


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
