"""Model admins for manifest app."""

from django.contrib import admin
from spring_manifest import models


@admin.register(models.DestinationZone)
class DestinationZoneAdmin(admin.ModelAdmin):
    """Model admin for DestinationZone model."""

    fields = ['name', 'code', 'format_code']
    list_display = ['name', 'code', 'format_code']
    list_display_links = ('name', )
    list_editable = ('code', 'format_code')

    def __repr__(self):
        return str(self.name)


@admin.register(models.CloudCommerceCountryID)
class CloudCommerceCountryIDAdmin(admin.ModelAdmin):
    """Model admin for CloudCommerceCountryID model."""

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
    """Model admin for SpringManifest model."""

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
    """Model admin for SpringOrder model."""

    fields = (
        'order_id', 'customer_name', 'date_recieved', 'dispatch_date',
        'country', 'manifest', 'service', 'canceled')
    list_display = (
        '__str__', 'order_id', 'customer_name', 'date_recieved',
        'dispatch_date', 'country', 'manifest', 'service', 'canceled')
    list_display_links = ('__str__', )
    list_editable = ('canceled', 'service')
    list_filter = ('date_recieved', 'service', 'dispatch_date', 'manifest')
    search_fields = (
        'order_id', 'customer_name', 'date_recieved', 'dispatch_date')

    def __repr__(self):
        return str(self.order_id)


@admin.register(models.ManifestPackage)
class ManifestPackageAdmin(admin.ModelAdmin):
    """Model admin for ManifestPackage model."""

    fields = ('package_number', 'order')
    list_display = ('__str__', 'package_number', 'order')


@admin.register(models.ManifestItem)
class ManifestItemAdmin(admin.ModelAdmin):
    """Model admin for ManifestItem model."""

    fields = ('package', 'item_id', 'quantity')
    list_display = ('__str__', 'package', 'item_id', 'quantity')


@admin.register(models.SecuredMailDestination)
class SecuredMailDestinationAdmin(admin.ModelAdmin):
    """Model admin for SecuredMailDestination model."""

    fields = ('name', 'manifest_row_number')
    list_display = ('id', 'name', 'manifest_row_number')
    list_editable = ('name', 'manifest_row_number')


@admin.register(models.Counter)
class CounterAdmin(admin.ModelAdmin):
    """Model admin for Counter model."""

    fields = ('name', 'count')
    list_display = ('__str__', 'name', 'count')
    list_editable = ('name', 'count')


@admin.register(models.CloudCommerceShippingRule)
class CloudCommerceShippingRuleAdmin(admin.ModelAdmin):
    """Model admin for the CloudCommerceShippingRule model."""

    fields = ('rule_id', 'name', 'full_name')
    list_display = ('__str__', 'rule_id', 'name', 'full_name')
    list_editable = ('rule_id', 'name', 'full_name')


@admin.register(models.ManifestService)
class ManifestServiceAdmin(admin.ModelAdmin):
    """Model admin for the ManifestService model."""

    fields = ('name', 'code', 'manifest_type', 'shipping_rules', 'enabled')
    list_display = (
        '__str__', 'name', 'code', 'manifest_type', 'shipping_rule_IDs',
        'enabled')
    list_editable = ('name', 'code', 'manifest_type', 'enabled')


@admin.register(models.SecuredMailService)
class SecuredMailServiceAdmin(admin.ModelAdmin):
    """Model admin for the SecuredMailService model."""

    fields = (
        'shipping_service', 'on_item_advice', 'on_manifest', 'on_docket',
        'docket_service', 'format', 'proof_of_delivery')
    list_display = (
        '__str__', 'shipping_service', 'on_item_advice', 'on_manifest',
        'on_docket', 'docket_service', 'format', 'proof_of_delivery')
    list_editable = (
        'shipping_service', 'on_item_advice', 'on_manifest', 'on_docket',
        'docket_service', 'format', 'proof_of_delivery')


@admin.register(models.ManifestType)
class ManifestTypeAdmin(admin.ModelAdmin):
    """Model admin for the ManifestType model."""

    fields = ('name', )
    list_display = ('__str__', 'name')
    list_editable = ('name', )
