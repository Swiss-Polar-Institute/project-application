from django.contrib import admin
import project_core.models


# Register your models here.


class StepAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['name', 'description',]


class StepDateAdmin(admin.ModelAdmin):
    list_display = ('step', 'date',)
    ordering = ['step', 'date',]


class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'message',)
    ordering = ['message_type',]


class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['name',]


class CallAdmin(admin.ModelAdmin):
    list_display = ('long_name', 'short_name', 'description', 'introductory_message', 'call_open_date', 'submission_deadline', 'budget_categories_list', 'budget_maximum',)
    ordering = ['long_name', 'short_name', 'call_open_date', 'submission_deadline', 'budget_maximum',]

    def budget_categories_list(self, obj):
        budget_categories = obj.budget_categories.all()

        return ", ".join([budget_categories.name for budget_category in budget_categories])

    filter_vertical = ('budget_categories', )


class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['description',]


class ProposalStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    ordering = ['description',]


class PersonTitleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ['title',]


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ['name',]


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('long_name', 'short_name', 'address', 'country',)
    ordering = ['long_name', 'short_name', 'country',]


class PersonAdmin(admin.ModelAdmin):
    list_display = ('academic_title', 'first_name', 'surname', 'organisations_list', 'group',)
    ordering = ['academic_title', 'first_name', 'surname',]

    def organisations_list(self, obj):
        organisations = obj.organisations.all()

        return ", ".join([organisations.name for organisation in organisations])


class ContactAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'work_telephone', 'mobile', 'person',)
    ordering = ['email_address', 'work_telephone', 'mobile', 'person',]


class GeographicalAreaAdmin(admin.ModelAdmin):
    list_display = ('area', 'definition',)
    ordering = ['area',]




admin.site.register(project_core.models.Step, StepAdmin)
admin.site.register(project_core.models.StepDate, StepDateAdmin)
admin.site.register(project_core.models.Message, MessageAdmin)
admin.site.register(project_core.models.BudgetCategory, BudgetCategoryAdmin)
admin.site.register(project_core.models.Call, CallAdmin)
admin.site.register(project_core.models.Keyword, KeywordAdmin)
admin.site.register(project_core.models.ProposalStatus, ProposalStatusAdmin)
admin.site.register(project_core.models.PersonTitle, PersonTitleAdmin)
admin.site.register(project_core.models.Country, CountryAdmin)
admin.site.register(project_core.models.Organisation, OrganisationAdmin)
admin.site.register(project_core.models.Person, PersonAdmin)
admin.site.register(project_core.models.Contact, ContactAdmin)
admin.site.register(project_core.models.GeographicalArea, GeographicalAreaAdmin)
