"""ModelAdmin classes for the inventory app."""

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from inventory import models


@admin.register(models.Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    """ModelAdmin for the Barcode model."""

    exclude_fields = ()
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

    exclude_fields = ()
    list_display = ("name", "active")
    list_filter = ("active",)
    list_editable = ("active",)
    search_fields = ("name",)


@admin.register(models.StockChange)
class StockChangeAdmin(admin.ModelAdmin):
    """Model admin for the Stock Change model."""

    exclude_fields = ()
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

    exclude_fields = ()
    list_display = ("__str__", "name", "timestamp", "export_file")
    date_hierarchy = "timestamp"


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Model admin for the Supplier model."""

    exclude_fields = ()
    list_display = ("name", "active")
    list_editable = ("active",)
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.SupplierContact)
class SupplierContactAdmin(admin.ModelAdmin):
    """Model admin for the SupplierContact model."""

    exclude_fields = ()
    list_display = ("__str__", "supplier", "name", "phone", "email", "notes")
    list_editable = ("supplier", "name", "phone", "email", "notes")
    search_fields = ("supplier__name", "name", "phone", "email")
    list_filter = ("supplier__active",)
    autocomplete_fields = ("supplier",)


@admin.register(models.PackageType)
class PackageTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the PackageType model."""

    exclude_fields = ()
    list_display = ("name", "large_letter_compatible", "ordering", "active")
    list_editable = ("large_letter_compatible", "active")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    """Model admin for the Brand model."""

    exclude_fields = ()
    list_display = ("name", "active")
    list_editable = ("active",)
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(models.Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Model admin for the Manufacturer model."""

    exclude_fields = ()
    list_display = ("name", "active")
    list_editable = ("active",)
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(models.ProductRange)
class ProductRangeAdmin(admin.ModelAdmin):
    """Model admin for the Product Range model."""

    exclude_fields = ("products", "images")
    list_display = (
        "__str__",
        "sku",
        "name",
        "is_end_of_line",
        "hidden",
        "status",
        "created_at",
        "modified_at",
    )
    list_editable = ("sku", "name", "is_end_of_line", "hidden", "status")
    search_fields = ("sku", "name")
    list_filter = ("is_end_of_line", "hidden", "status")
    date_hierarchy = "created_at"


@admin.register(models.VariationOption)
class VariationOptionAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the Product Option model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.ListingAttribute)
class ListingAttributeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the ListingAttribute model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.VATRate)
class VATRateAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the VATRate model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "percentage")
    list_editable = ("name", "percentage")
    search_fields = ("name",)


@admin.register(models.BaseProduct)
class BaseProductAdmin(admin.ModelAdmin):
    """Model admin for the BaseProduct model."""

    exclude_fields = ()
    list_display = ("sku", "product_range")
    list_filter = ("product_range__status", "product_range__is_end_of_line")
    search_fields = ("sku", "product_range__sku", "product_range__name")
    autocomplete_fields = (
        "product_range",
        "package_type",
    )
    date_hierarchy = "created_at"


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    """Model admin for the Product model."""

    exclude_fields = ()
    list_display = (
        "sku",
        "full_name",
        "created_at",
        "modified_at",
        "is_end_of_line",
        "range_order",
    )
    list_filter = ("is_end_of_line",)
    search_fields = (
        "sku",
        "product_range__name",
        "supplier_sku",
        "product_range__sku",
    )
    list_editable = ("range_order",)
    autocomplete_fields = (
        "product_range",
        "supplier",
        "vat_rate",
        "brand",
        "manufacturer",
        "package_type",
        "gender",
    )
    date_hierarchy = "created_at"


@admin.register(models.Gender)
class GenderAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the PackageType model."""

    exclude_fields = ()
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Model admin for the ProductImage model."""

    exclude_fields = ()
    list_display = (
        "product_id",
        "range_sku",
        "sku",
        "cloud_commerce_name",
        "position",
        "image_file",
    )
    search_fields = ("product_id", "range_sku", "sku", "cloud_commerce_name")


@admin.register(models.ProductImageLink)
class ProductImageLinkAdmin(admin.ModelAdmin):
    """Model admin for the ProductImageLink model."""

    exclude_fields = ()
    list_display = ("__str__", "product", "image", "ordering", "active")
    list_editable = ("ordering", "active")
    search_fields = (
        "product__sku",
        "product__product_range__sku",
        "product__product_range__name",
    )
    list_select_related = ("product", "product__product_range", "image")


@admin.register(models.ProductRangeImageLink)
class ProductRangeImageLinkAdmin(admin.ModelAdmin):
    """Model admin for the ProductRangeImageLink model."""

    exclude_fields = ()
    list_display = ("product_range", "image", "ordering", "active")
    list_editable = ("ordering", "active")
    search_fields = (
        "product_range__sku",
        "product_range__name",
    )
    list_select_related = ("product_range", "image")
