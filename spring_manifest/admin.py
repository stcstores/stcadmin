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
    list_display_links = ('cc_id', )
    list_editable = ('name', 'iso_code', 'zone', 'valid_spring_destination')
    search_fields = ('name', )

    def __repr__(self):
        return str(self.name)


@admin.register(models.SpringManifest)
class SpringManifestAdmin(admin.ModelAdmin):
    fields = ('manifest_type', 'time_filed', 'manifest_file')
    list_display = (
        'id', '__str__', 'manifest_type', 'time_created', 'time_filed',
        'manifest_file')
    list_display_links = ('__str__', )
    list_editable = ('manifest_type', )


@admin.register(models.SpringOrder)
class SpringOrderAdmin(admin.ModelAdmin):
    fields = (
        'id', 'order_id', 'customer_name', 'date_recieved', 'dispatch_date',
        'country', 'product_count', 'package_count', 'manifest', 'service',
        'canceled')
    list_display = (
        '__str__', 'order_id', 'customer_name', 'date_recieved',
        'dispatch_date', 'country', 'product_count', 'package_count',
        'manifest', 'service', 'canceled')
    list_display_links = ('__str__', )
    list_editable = ('product_count', 'package_count', 'canceled')
    list_filter = ('date_recieved', 'dispatch_date', 'service', 'manifest')
    search_fields = (
        'order_id', 'customer_name', 'date_recieved', 'dispatch_date')

    def __repr__(self):
        return str(self.order_id)
