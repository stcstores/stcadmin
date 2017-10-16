from django.contrib import admin

from spring_manifest import models


@admin.register(models.DestinationZone)
class DestinationZoneAdmin(admin.ModelAdmin):

    fields = ['name', 'code', 'format_code']
    list_display = ['name', 'code', 'format_code']
    list_display_links = ('name', )
    list_editable = ('code', 'format_code')

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


@admin.register(models.SpringOrder)
class SpringOrderAdmin(admin.ModelAdmin):
    fields = (
        'order_id', 'customer_name', 'date_recieved', 'dispatch_date',
        'manifest')
    list_display = (
        'order_id', 'customer_name', 'date_recieved', 'dispatch_date',
        'manifest')
    list_display_links = ('order_id',)

    def __repr__(self):
        return str(self.order_id)
