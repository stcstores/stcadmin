from django.contrib import admin

from spring_manifest import models


@admin.register(models.DestinationZone)
class DestinationZoneAdmin(admin.ModelAdmin):

    fields = ['name', 'code']
    list_display = ['name', 'code']

    def __repr__(self):
        return str(self.name)


@admin.register(models.CloudCommerceCountryID)
class CloudCommerceCountryIDAdmin(admin.ModelAdmin):
    fields = ('cc_id', 'name', 'iso_code', 'zone')
    list_display = ('cc_id', 'name', 'iso_code', 'zone')
    list_display_links = ('cc_id',)
    list_editable = ('name', 'iso_code', 'zone')

    def __repr__(self):
        return str(self.name)
