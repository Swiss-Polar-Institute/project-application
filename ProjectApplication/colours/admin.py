from django.contrib import admin

from colours.forms import ColourForm
from colours.models import Colour, ColourPair


class ColourAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    ordering = ['name', 'hex_code']
    form = ColourForm


class ColourPairAdmin(admin.ModelAdmin):
    list_display = ('description', 'background', 'text')
    ordering = ['description', ]


admin.site.register(Colour, ColourAdmin)
admin.site.register(ColourPair, ColourPairAdmin)
