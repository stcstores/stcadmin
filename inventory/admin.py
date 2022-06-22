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


@admin.register(models.BaseProduct)
class BaseProductAdmin(admin.ModelAdmin):
    """Model admin for the BaseProduct model."""

    exclude_fields = ()
    list_display = ("sku", "product_range")
    list_filter = ("product_range__status", "product_range__is_end_of_line")
    search_fields = ("sku", "product_range__sku", "product_range__name")
    autocomplete_fields = ("product_range", "package_type")
    list_select_related = ("product_range", "package_type")
    date_hierarchy = "created_at"


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    """ModelAdmin for the Bay model."""

    exclude_fields = ()
    list_display = ("name", "active")
    list_filter = ("active",)
    list_editable = ("active",)
    search_fields = ("name",)


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    """Model admin for the Brand model."""

    exclude_fields = ()
    list_display = ("name", "active")
    list_editable = ("active",)
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(models.CombinationProduct)
class CombinationProductAdmin(admin.ModelAdmin):
    """Model admin for the CombinationProduct model."""

    exclude_fields = ()
    list_display = ("sku", "product_range")
    list_filter = ("product_range__status", "product_range__is_end_of_line")
    search_fields = ("sku", "product_range__sku", "product_range__name")
    autocomplete_fields = ("product_range", "package_type")
    list_select_related = ("product_range", "package_type")
    date_hierarchy = "created_at"


@admin.register(models.CombinationProductLink)
class CombinationProductLinkAdmin(admin.ModelAdmin):
    """Model admin for the CombinationProductLink model."""

    exclude_fields = ()
    list_display = ("__str__", "product", "combination_product", "quantity")
    search_fields = (
        "product__sku",
        "product__product_range__sku",
        "product__product_range__name",
        "combination_product__sku",
        "combination_product__product_range__sku",
        "combination_product__product_range__name",
    )
    autocomplete_fields = ("product", "combination_product")
    list_select_related = ("product", "combination_product")


@admin.register(models.ListingAttribute)
class ListingAttributeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the ListingAttribute model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.ListingAttributeValue)
class ListingAttributeValueAdmin(admin.ModelAdmin):
    """Model admin for the ListingAttributeValue model."""

    exclude_fields = ()
    list_display = ("__str__", "product", "listing_attribute", "value")
    search_fields = (
        "product__sku",
        "product__product_range__sku",
        "product__product_range__name",
        "listing_attribute__name",
        "value",
    )
    list_filter = ("listing_attribute",)
    autocomplete_fields = ("product", "listing_attribute")
    list_select_related = ("product", "listing_attribute")


@admin.register(models.Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Model admin for the Manufacturer model."""

    exclude_fields = ()
    list_display = ("name", "active")
    list_editable = ("active",)
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(models.MultipackProduct)
class MultipackProductAdmin(admin.ModelAdmin):
    """Model admin for the MultipackProduct model."""

    exclude_fields = ()
    list_display = ("sku", "product_range", "base_product", "quantity")
    list_filter = ("product_range__status", "product_range__is_end_of_line")
    search_fields = (
        "sku",
        "product_range__sku",
        "product_range__name",
        "base_product__product_range__name",
        "base_product__sku",
    )
    autocomplete_fields = ("product_range", "base_product", "package_type")
    list_select_related = ("product_range", "base_product", "package_type")
    date_hierarchy = "created_at"


@admin.register(models.PackageType)
class PackageTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the PackageType model."""

    exclude_fields = ()
    list_display = (
        "name",
        "large_letter_compatible",
        "description",
        "ordering",
        "active",
    )
    list_editable = ("large_letter_compatible", "description", "active")
    list_filter = ("active",)
    search_fields = ("name",)


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
    list_select_related = (
        "product_range",
        "supplier",
        "vat_rate",
        "brand",
        "manufacturer",
        "package_type",
    )
    autocomplete_fields = (
        "product_range",
        "supplier",
        "vat_rate",
        "brand",
        "manufacturer",
        "package_type",
    )
    date_hierarchy = "created_at"


@admin.register(models.ProductBayHistory)
class ProductBayHistoryAdmin(admin.ModelAdmin):
    """Model admin for the ProductBayHistory model."""

    exclude_fields = ()
    list_display = ("__str__", "user", "timestamp", "product", "bay", "change")
    autocomplete_fields = ("product", "bay", "user")
    list_select_related = ("product", "bay", "user")
    list_filter = ("user",)
    search_fields = (
        "product__sku",
        "product_range__sku",
        "product_range__name",
        "bay__name",
    )
    date_hierarchy = "timestamp"


@admin.register(models.ProductExport)
class ProductExportAdmin(admin.ModelAdmin):
    """Model admin for the Product Export model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "timestamp", "export_file")
    date_hierarchy = "timestamp"


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Model admin for the ProductImage model."""

    exclude_fields = ()
    list_display = ("image_file",)
    search_fields = ("image_file",)


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


@admin.register(models.StockLevelHistory)
class StockLevelHistoryAdmin(admin.ModelAdmin):
    """Model admin for the StockLevelHistory model."""

    exclude_fields = ()
    list_display = (
        "__str__",
        "product",
        "source",
        "user",
        "timestamp",
        "stock_level",
        "previous_change",
    )
    search_fields = (
        "product__sku",
        "product_range__sku",
        "product__range__name" "user__first_name",
        "user__last_name",
        "user__username",
    )
    list_filter = ("user",)
    date_hierarchy = "timestamp"
    autocomplete_fields = ("product", "user", "previous_change")
    list_select_related = ("product", "user", "previous_change")


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
    list_select_related = ("supplier",)


@admin.register(models.VATRate)
class VATRateAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the VATRate model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "percentage")
    list_editable = ("name", "percentage")
    search_fields = ("name",)


@admin.register(models.VariationOption)
class VariationOptionAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the Product Option model."""

    exclude_fields = ()
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)


@admin.register(models.VariationOptionValue)
class VariationOptionValueAdmin(admin.ModelAdmin):
    """Model admin for the VariationOptionValue model."""

    exclude_fields = ()
    list_display = ("__str__", "product", "variation_option", "value")
    search_fields = (
        "product__sku",
        "product__product_range__sku",
        "product__product_range__name",
        "variation_option__name",
        "value",
    )
    list_filter = ("variation_option",)
    autocomplete_fields = ("product", "variation_option")
    list_select_related = ("product", "variation_option")
