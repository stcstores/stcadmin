from django.contrib import admin
from price_calculator import models


@admin.register(models.DestinationCountry)
class DestinationCountryAdmin(admin.ModelAdmin):
    fields = ('name', )
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(models.PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    fields = ('name', )
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(models.ShippingPrice)
class ShippingPriceAdmin(admin.ModelAdmin):
    fields = (
        'name', 'country', 'package_type', 'min_weight', 'max_weight',
        'min_price', 'max_price', 'item_price', 'kilo_price', 'vat_rates')
    list_display = (
        '__str__', 'name', 'package_type_string', 'country', 'min_weight',
        'max_weight', 'min_price', 'max_price', 'item_price', 'kilo_price')
    list_display_links = ('__str__', )
    list_editable = (
        'name', 'country', 'min_weight', 'max_weight', 'min_price',
        'max_price', 'item_price', 'kilo_price')
    list_filter = ('package_type', 'country', 'vat_rates')
    search_fields = ('name', )


@admin.register(models.VATRate)
class VATRateAdmin(admin.ModelAdmin):
    fields = ('name', 'cc_id', 'percentage')
    list_display = ('__str__', 'name', 'cc_id', 'percentage')
    list_display_links = ('__str__', )
    list_editable = ('name', 'cc_id', 'percentage')
    search_fields = ('name', )
