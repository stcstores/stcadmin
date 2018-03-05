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


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    fields = ('warehouse_id', 'name')
    list_display = ('warehouse_id', 'name')
    search_fields = ('name', )


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    fields = ('bay_id', 'name', 'warehouse')
    list_display = ('bay_id', '__str__', 'name', 'warehouse')
    search_fields = ('name', )
    list_filter = ('warehouse', )
