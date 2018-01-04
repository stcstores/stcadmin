from django.contrib import admin
from stock_check import models


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    fields = ('warehouse_id', 'name')
    list_display = ('__str__', 'warehouse_id', 'name')
    list_display_links = ('__str__', )
    list_editable = ('warehouse_id', 'name')
    search_fields = ('warehouse_id', 'name')


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    fields = ('bay_id', 'name', 'warehosue')
    list_display = ('__str__', 'bay_id', 'name', 'warehouse')
    list_display_links = ('__str__', )
    list_editable = ('bay_id', 'name', 'warehouse')
    search_fields = ('bay_id', 'name')
    list_filter = ('warehouse', )


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ('range_id', 'product_id', 'sku', 'bays')
    list_display = ('__str__', 'range_id', 'product_id', 'sku', 'bay_names')
    list_display_links = ('__str__', )
    list_editable = ('range_id', 'product_id', 'sku')
    search_fields = ('range_id', 'product_id', 'sku')
