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


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    """ModelAdmin for the Bay model."""

    fields = ("name",)
    list_display = ("__str__", "name")
    search_fields = ("name",)


@admin.register(models.StockChange)
class StockChangeAdmin(admin.ModelAdmin):
    """Model admin for the Stock Change model."""

    fields = (
        "user",
        "timestamp",
        "product_sku",
        "stock_before",
        "stock_after",
    )
    list_display = (
        "__str__",
        "get_user_name",
        "timestamp",
        "product_sku",
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
class ProductExportAdmin(admin.ModelAdmin):
    """Model admin for the Product Export model."""

    fields = ("name", "timestamp", "export_file")
    list_display = ("__str__", "name", "timestamp", "export_file")
    date_hierarchy = "timestamp"


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Model admin for the Supplier model."""

    fields = ("name", "active")
    list_display = (
        "__str__",
        "name",
        "active",
    )
    list_editable = ("name", "active")
    search_fields = ("name",)


@admin.register(models.SupplierContact)
class SupplierContactAdmin(admin.ModelAdmin):
    """Model admin for the SupplierContact model."""

    fields = ("supplier", "name", "phone", "email", "notes")
    list_display = ("__str__", "supplier", "name", "phone", "email", "notes")
    list_editable = ("supplier", "name", "phone", "email", "notes")
    search_fields = ("name", "phone", "email")
    list_filter = ("supplier",)


@admin.register(models.PackageType)
class PackageTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the PackageType model."""

    fields = (
        "name",
        "large_letter_compatible",
    )
    list_display = (
        "name",
        "large_letter_compatible",
    )
    list_editable = ("large_letter_compatible",)


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    """Model admin for the Brand model."""

    fields = ("name",)
    list_display = ("name",)


@admin.register(models.Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Model admin for the Manufacturer model."""

    fields = ("name",)
    list_display = ("name",)


@admin.register(models.ProductRange)
class ProductRangeAdmin(admin.ModelAdmin):
    """Model admin for the Product Range model."""

    fields = (
        "sku",
        "name",
        "description",
        "amazon_bullet_points",
        "amazon_search_terms",
        "end_of_line",
        "hidden",
        "status",
    )
    list_display = (
        "__str__",
        "sku",
        "name",
        "product_count",
        "end_of_line",
        "hidden",
        "status",
    )
    list_editable = (
        "sku",
        "name",
        "end_of_line",
        "hidden",
        "status",
    )
    search_fields = ("sku", "name")
    list_filter = ("end_of_line", "hidden", "status")


@admin.register(models.VariationOption)
class VariationOptionAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the Product Option model."""

    fields = ("name", "ordering", "active")
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.ListingAttribute)
class ListingAttributeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the ListingAttribute model."""

    fields = ("name", "ordering", "active")
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.VATRate)
class VATRateAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the VATRate model."""

    fields = ("name", "percentage")
    list_display = ("__str__", "name", "percentage")
    list_editable = ("name", "percentage")


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    """Model admin for the Product model."""

    fields = (
        "product_range",
        "sku",
        "supplier",
        "supplier_sku",
        "barcode",
        "purchase_price",
        "vat_rate",
        "retail_price",
        "brand",
        "manufacturer",
        "package_type",
        "bays",
        "weight_grams",
        "length_mm",
        "height_mm",
        "width_mm",
        "gender",
        "end_of_line",
        "range_order",
    )
    list_display = (
        "sku",
        "full_name",
        "date_created",
        "last_modified",
        "end_of_line",
        "range_order",
    )
    list_display_links = ("sku",)
    list_filter = ("end_of_line",)
    search_fields = (
        "sku",
        "product_range__name",
        "supplier_sku",
        "product_range__sku",
    )
    list_editable = ("range_order",)


@admin.register(models.Gender)
class GenderAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the PackageType model."""

    fields = ("name",)
    list_display = ("name",)


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Model admin for the ProductImage model."""

    fields = (
        "product_id",
        "range_sku",
        "sku",
        "cloud_commerce_name",
        "postition",
        "image_file",
    )
    list_display = (
        "product_id",
        "range_sku",
        "sku",
        "cloud_commerce_name",
        "position",
        "image_file",
    )
    search_fields = ("product_id", "range_sku", "sku", "cloud_commerce_name")
