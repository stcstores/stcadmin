"""ModelAdmin classes for the inventory app."""

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from inventory import models


@admin.register(models.Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    """ModelAdmin for the Barcode model."""

    fields = ("barcode", "added_on", "used_on", "used_by", "used_for")
    list_display = (
        "barcode",
        "available",
        "added_on",
        "used_on",
        "used_by",
        "used_for",
    )
    search_fields = ("barcode", "used_for")
    list_filter = ("available", "used_by")


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """ModelAdmin for the Warehouse model."""

    fields = ("warehouse_ID", "name", "abriviation")
    list_display = ("warehouse_ID", "name", "abriviation")
    search_fields = ("name", "abriviation")


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    """ModelAdmin for the Bay model."""

    fields = ("bay_ID", "name", "warehouse", "is_default")
    list_display = ("bay_ID", "__str__", "name", "warehouse", "is_default")
    search_fields = ("name",)
    list_filter = ("warehouse",)


@admin.register(models.StockChange)
class StockChangeAdmin(admin.ModelAdmin):
    """Model admin for the Stock Change model."""

    fields = (
        "user",
        "timestamp",
        "product_sku",
        "product_id",
        "stock_before",
        "stock_after",
    )
    list_display = (
        "__str__",
        "get_user_name",
        "timestamp",
        "product_sku",
        "product_id",
        "stock_before",
        "stock_after",
    )
    search_fields = (
        "product_sku",
        "product_sku",
        "user__first_name",
        "user__last_name",
        "user__username",
    )
    list_filter = ("user",)
    date_hierarchy = "timestamp"


@admin.register(models.ProductExport)
class ProductOptionAdminProductExportAdmin(admin.ModelAdmin):
    """Model admin for the Product Export model."""

    fields = ("name", "timestamp", "export_file")
    list_display = ("__str__", "name", "timestamp", "export_file")
    date_hierarchy = "timestamp"


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Model admin for the Supplier model."""

    fields = ("name", "product_option_value_ID", "factory_ID", "inactive")
    list_display = (
        "__str__",
        "name",
        "product_option_value_ID",
        "factory_ID",
        "inactive",
    )
    list_editable = ("name", "product_option_value_ID", "factory_ID", "inactive")
    search_fields = ("name",)


@admin.register(models.SupplierContact)
class SupplierContactAdmin(admin.ModelAdmin):
    """Model admin for the SupplierContact model."""

    fields = ("supplier", "name", "phone", "email", "notes")
    list_display = ("__str__", "supplier", "name", "phone", "email", "notes")
    list_editable = ("supplier", "name", "phone", "email", "notes")
    search_fields = ("name", "phone", "email")
    list_filter = ("supplier",)


class ProductOptionAdmin(admin.ModelAdmin):
    """Model admin for the ProductOptionModel abstract model."""

    fields = ("name", "product_option_value_ID", "inactive")
    list_display = ("__str__", "name", "product_option_value_ID", "inactive")
    list_editable = ("name", "product_option_value_ID", "inactive")
    search_fields = ("name", "product_option_value_ID")


@admin.register(models.Department)
class DepartmentAdmin(ProductOptionAdmin):
    """Model admin for the Department model."""

    fields = ("name", "abriviation", "product_option_value_ID", "inactive")
    list_display = (
        "__str__",
        "name",
        "abriviation",
        "product_option_value_ID",
        "inactive",
    )
    list_editable = (
        "name",
        "name",
        "abriviation",
        "product_option_value_ID",
        "inactive",
    )
    search_fields = ("name", "abriviation", "product_option_value_ID")


@admin.register(models.PackageType)
class PackageTypeAdmin(SortableAdminMixin, ProductOptionAdmin):
    """Model admin for the PackageType model."""

    pass


@admin.register(models.InternationalShipping)
class InternationalShippingAdmin(SortableAdminMixin, ProductOptionAdmin):
    """Model admin for the InternationalShipping model."""

    pass
