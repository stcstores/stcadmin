"""ModelAdmin classes for the inventory app."""

from django.contrib import admin
from orderable.admin import OrderableAdmin

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

    fields = ("warehouse_ID", "name", "abriviation")
    list_display = ("warehouse_ID", "name", "abriviation")
    search_fields = ("name", "abriviation")


@admin.register(models.Bay)
class BayAdmin(admin.ModelAdmin):
    """ModelAdmin for the Bay model."""

    fields = ("bay_ID", "name", "warehouse")
    list_display = ("bay_ID", "__str__", "name", "warehouse")
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


class BaseNonListingProductOptionModel(admin.ModelAdmin):
    """Model admin for the BaseNonListingProductOptionModel abstract model."""

    fields = ("name", "product_option_value_ID", "inactive")
    list_display = ("__str__", "name", "product_option_value_ID", "inactive")
    list_editable = ("name", "product_option_value_ID", "inactive")
    search_fields = ("name", "product_option_value_ID")


class OrderableProductOptionAdmin(OrderableAdmin, BaseNonListingProductOptionModel):
    """Model admin for orderable product options."""

    list_display = BaseNonListingProductOptionModel.list_display + (
        "sort_order_display",
    )


@admin.register(models.Department)
class DepartmentAdmin(BaseNonListingProductOptionModel):
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
class PackageTypeAdmin(OrderableProductOptionAdmin):
    """Model admin for the PackageType model."""

    pass


@admin.register(models.InternationalShipping)
class InternationalShippingAdmin(OrderableProductOptionAdmin):
    """Model admin for the InternationalShipping model."""

    pass


@admin.register(models.Brand)
class BrandAdmin(BaseNonListingProductOptionModel):
    """Model admin for the Brand model."""

    pass


@admin.register(models.Manufacturer)
class ManufacturerAdmin(BaseNonListingProductOptionModel):
    """Model admin for the Manufacturer model."""

    pass


@admin.register(models.ProductRange)
class ProductRangeAdmin(admin.ModelAdmin):
    """Model admin for the Product Range model."""

    fields = (
        "range_ID",
        "SKU",
        "name",
        "department",
        "variation_options",
        "description",
        "amazon_bullet_points",
        "amazon_search_terms",
        "end_of_line",
        "hidden",
    )
    list_display = (
        "__str__",
        "range_ID",
        "SKU",
        "name",
        "department",
        "product_count",
        "end_of_line",
        "hidden",
    )
    list_editable = ("range_ID", "SKU", "name", "department", "end_of_line", "hidden")
    search_fields = ("range_ID", "SKU", "name")
    list_filter = ("department", "end_of_line", "hidden")


@admin.register(models.ProductOption)
class ProductOptionAdmin(OrderableAdmin):
    """Model admin for the Product Option model."""

    fields = ("name", "product_option_ID", "inactive")
    list_display = (
        "__str__",
        "name",
        "product_option_ID",
        "inactive",
        "sort_order_display",
    )
    list_editable = ("name", "product_option_ID", "inactive")
    search_fields = ("name", "product_option_ID")
    list_filter = ("inactive",)


@admin.register(models.ProductOptionValue)
class ProductOptionValueAdmin(admin.ModelAdmin):
    """Model admin for the ProductOptionValue model."""

    fields = ("value", "product_option", "product_option_value_ID")
    list_display = ("__str__", "value", "product_option", "product_option_value_ID")
    list_editable = ("value", "product_option", "product_option_value_ID")
    list_filter = ("product_option",)
    search_fields = ("value",)


@admin.register(models.VATRate)
class VATRateAdmin(OrderableAdmin):
    """Model admin for the VATRate model."""

    fields = ("VAT_rate_ID", "name", "percentage")
    list_display = (
        "__str__",
        "VAT_rate_ID",
        "name",
        "percentage",
        "sort_order_display",
    )
    list_editable = ("VAT_rate_ID", "name", "percentage")


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    """Model admin for the Product model."""

    fields = (
        "product_ID",
        "product_range",
        "SKU",
        "name",
        "supplier",
        "supplier_SKU",
        "barcode",
        "purchase_price",
        "VAT_rate",
        "price",
        "retail_price",
        "brand",
        "manufacturer",
        "package_type",
        "international_shipping",
        "bays",
        "weight_grams",
        "length_mm",
        "height_mm",
        "width_mm",
        "product_options",
        "multipack",
        "end_of_line",
        "status",
    )
    list_display = (
        "range_SKU",
        "SKU",
        "name",
        "department",
        "multipack",
        "date_created",
        "last_modified",
        "status",
        "end_of_line",
    )
    list_display_links = ("SKU", "name")
    list_filter = ("product_range__department", "end_of_line")
    search_fields = ("SKU", "name", "supplier_SKU", "product_range__SKU")
