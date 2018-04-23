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
    fields = (
        'cc_id', 'name', 'iso_code', 'zone', 'currency_code',
        'valid_spring_destination', 'secured_mail_destination')
    list_display = (
        'cc_id', 'name', 'iso_code', 'zone', 'currency_code',
        'valid_spring_destination', 'secured_mail_destination')
    list_display_links = ('cc_id', )
    list_editable = (
        'name', 'iso_code', 'zone', 'currency_code',
        'valid_spring_destination', 'secured_mail_destination')
    search_fields = ('name', 'secured_mail_destination__name')
    list_filter = ('zone', 'secured_mail_destination__name')

    def __repr__(self):
        return str(self.name)


@admin.register(models.SpringManifest)
class SpringManifestAdmin(admin.ModelAdmin):
    fields = (
        'manifest_type', 'time_filed', 'manifest_file', 'item_advice_file',
        'status', 'errors')
    list_display = (
        'id', '__str__', 'manifest_type', 'time_created', 'time_filed',
        'manifest_file', 'item_advice_file', 'status')
    list_display_links = ('__str__', )
    list_editable = ('manifest_type', 'status')


@admin.register(models.SpringOrder)
class SpringOrderAdmin(admin.ModelAdmin):
    fields = (
        'id', 'order_id', 'customer_name', 'date_recieved', 'dispatch_date',
        'country', 'manifest', 'service', 'canceled')
    list_display = (
        '__str__', 'order_id', 'customer_name', 'date_recieved',
        'dispatch_date', 'country', 'manifest', 'service', 'canceled')
    list_display_links = ('__str__', )
    list_editable = ('canceled', )
    list_filter = ('date_recieved', 'dispatch_date', 'service', 'manifest')
    search_fields = (
        'order_id', 'customer_name', 'date_recieved', 'dispatch_date')

    def __repr__(self):
        return str(self.order_id)


@admin.register(models.SpringPackage)
class SpringPackageAdmin(admin.ModelAdmin):
    fields = ('package_number', 'order')
    list_display = ('__str__', 'package_number', 'order')


@admin.register(models.SpringItem)
class SpringItemAdmin(admin.ModelAdmin):
    fields = ('package', 'item_id', 'quantity')
    list_display = ('__str__', 'package', 'item_id', 'quantity')


@admin.register(models.SecuredMailDestination)
class SecuredMailDestinationAdmin(admin.ModelAdmin):
    fields = ('name', 'manifest_row_number')
    list_display = ('id', 'name', 'manifest_row_number')
    list_editable = ('name', 'manifest_row_number')


@admin.register(models.Counter)
class CounterAdmin(admin.ModelAdmin):
    fields = ('name', 'count')
    list_display = ('__str__', 'name', 'count')
    list_editable = ('name', 'count')
