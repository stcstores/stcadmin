"""ModelAdmin classes for the inventory app."""

from django.contrib import admin
from orderable.admin import OrderableAdmin

from inventory import models


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

    fields = ("bay_ID", "name", "warehouse", "is_default")
    list_display = ("bay_ID", "__str__", "name", "warehouse", "is_default")
    list_editable = ("is_default",)
    search_fields = ("name", "bay_ID")
    list_filter = ("warehouse", "is_default")


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

    fields = OrderableProductOptionAdmin.fields + ("large_letter_compatible",)
    list_display = OrderableProductOptionAdmin.list_display + (
        "large_letter_compatible",
    )
    list_editable = OrderableProductOptionAdmin.list_editable + (
        "large_letter_compatible",
    )


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
        "multipack",
        "gender",
        "end_of_line",
        "status",
        "range_order",
    )
    list_display = (
        "range_SKU",
        "SKU",
        "full_name",
        "department",
        "multipack",
        "date_created",
        "last_modified",
        "status",
        "end_of_line",
        "range_order",
    )
    list_display_links = ("SKU",)
    list_filter = ("product_range__department", "end_of_line")
    search_fields = (
        "SKU",
        "product_range__name",
        "supplier_SKU",
        "product_range__SKU",
        "product_ID",
        "product_range__range_ID",
    )
    list_editable = ("range_order",)


@admin.register(models.ProductRangeSelectedOption)
class ProductRangeSelectedOptionAdmin(admin.ModelAdmin):
    """Model admin for the ProductRangeSelectedOptions model."""

    fields = ("product_range", "product_option", "variation")
    list_display = ("product_range", "product_option", "variation")
    list_editable = ("variation",)
    list_filter = ("product_option", "variation")
    search_fields = (
        "product_range__name",
        "product_range__SKU",
        "product_range__range_ID",
        "product_option__name",
    )


@admin.register(models.ProductOptionValueLink)
class ProductOptionValueLinkAdmin(admin.ModelAdmin):
    """Model admin for the ProductOptionValueLink model."""

    fields = ("product", "product_option_value")
    list_display = ("product", "product_option_value")
    list_filter = ("product_option_value__product_option",)
    search_fields = (
        "product__SKU",
        "product__product_range__SKU",
        "product__product_range__name",
        "product__product_range__range_ID",
        "product_option_value__value",
        "product__product_ID",
    )


@admin.register(models.Gender)
class GenderAdmin(OrderableProductOptionAdmin):
    """Model admin for the PackageType model."""

    fields = OrderableProductOptionAdmin.fields + ("readable_name",)
    list_display = OrderableProductOptionAdmin.list_display + ("readable_name",)
    list_editable = OrderableProductOptionAdmin.list_editable + ("readable_name",)


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Model admin for the ProductImage model."""

    fields = ("image_ID", "product", "filename", "URL", "position")
    list_display = ("__str__", "image_ID", "product", "filename", "URL", "position")
    list_display_links = ("__str__",)
    search_fields = (
        "product__SKU",
        "product__product_range__SKU",
        "product__product_range__name",
        "product__product_range__range_ID",
        "product__product_ID",
    )


@admin.register(models.ProductEdit)
class ProductEditAdmin(admin.ModelAdmin):
    """Model admin for the ProductEdit model."""

    fields = ("user", "product_range", "partial_product_range", "product_option_values")
    list_display = ("__str__", "user", "product_range", "partial_product_range")


@admin.register(models.PartialProductRange)
class PartialProductRangeAdmin(ProductRangeAdmin):
    """Model admin for the PartialProductRange model."""

    pass


@admin.register(models.PartialProduct)
class PartialProductAdmin(ProductAdmin):
    """Model admin for the PartialProduct model."""

    pass


@admin.register(models.PartialProductOptionValueLink)
class PartialProductOptionValueLinkAdmin(ProductOptionValueLinkAdmin):
    """Model admin for the PartialProductOptionValueLink model."""

    pass


@admin.register(models.PartialProductRangeSelectedOption)
class PartialProductRangeSelectedOptionAdmin(ProductRangeSelectedOptionAdmin):
    """Model admin for the PartialProductRangeSelectedOption model."""

    pass
