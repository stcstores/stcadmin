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
    fields = ('cc_id', 'name', 'iso_code', 'zone', 'valid_spring_destination')
    list_display = (
        'cc_id', 'name', 'iso_code', 'zone', 'valid_spring_destination')
    list_display_links = ('cc_id',)
    list_editable = ('name', 'iso_code', 'zone', 'valid_spring_destination')

    def __repr__(self):
        return str(self.name)


@admin.register(models.ManifestedOrder)
class ManifestedOrderAdmin(admin.ModelAdmin):
    fields = ('order_id', 'service_code', 'country', 'manifest_time')
    list_display = ('order_id', 'service_code', 'country', 'manifest_time')
    list_display_links = ('order_id',)
    list_editable = ('service_code', 'country')

    def __repr__(self):
        return str(self.order_id)
