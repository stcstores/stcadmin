from django.contrib import admin

from inventory import models


@admin.register(models.STCAdminImage)
class STCAdminImageAdmin(admin.ModelAdmin):

    fields = ['range_id', 'image']
    list_display = ['id', '__str__', 'range_id', 'image']
    list_display_links = ('__str__', )
    list_editable = ('range_id', 'image')

    def __repr__(self):
        return str(self.name)


@admin.register(models.Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    fields = ('barcode', 'used')
    list_display = ('barcode', 'used')
    search_fields = ('barcode', )
    list_filter = ('used', )

    def __repr__(self):
        return str(self.barcode)


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
        'country', 'package_type', 'min_weight', 'max_weight',
        'item_price', 'kilo_price')
    list_display = (
        '__str__', 'country', 'min_weight', 'max_weight',
        'item_price', 'kilo_price')
    list_display_links = ('__str__', )
    list_editable = (
        'country', 'min_weight', 'max_weight',
        'item_price', 'kilo_price')
    list_filter = ('package_type', )
    search_fields = ('country', )
