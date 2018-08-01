"""ModelAdmin classes for the inventory app."""

from django.contrib import admin

from inventory import models


@admin.register(models.STCAdminImage)
class STCAdminImageAdmin(admin.ModelAdmin):
    """ModelAdmin for the STCAdminImage model."""

    fields = ["range_id", "image"]
    list_display = ["id", "__str__", "range_id", "image"]
    list_display_links = ("__str__",)
    list_editable = ("range_id", "image")

    def __repr__(self):
        return str(self.name)


@admin.register(models.Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    """ModelAdmin for the Barcode model."""

    fields = ("barcode", "used")
    list_display = ("barcode", "used")
    search_fields = ("barcode",)
    list_filter = ("used",)

    def __repr__(self):
        return str(self.barcode)


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """ModelAdmin for the Warehouse model."""

    fields = ("warehouse_id", "name", "abriviation")
    list_display = ("warehouse_id", "name", "abriviation")
    search_fields = ("name", "abriviation")


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    """ModelAdmin for the Bay model."""

    fields = ("bay_id", "name", "warehouse")
    list_display = ("bay_id", "__str__", "name", "warehouse")
    search_fields = ("name",)
    list_filter = ("warehouse",)
