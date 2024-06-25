"""Model Admin for the FBA app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from fba import models


@admin.register(models.FBARegion)
class FBARegionAdmin(admin.ModelAdmin):
    """Model admin for the FBARegion model."""

    exclude = ()
    list_display = [
        "name",
        "active",
        "country",
        "postage_price",
        "postage_per_kg",
        "postage_overhead_g",
        "min_shipping_cost",
        "max_weight",
        "max_size",
        "placement_fee",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
        "expiry_date_required",
        "position",
    ]
    list_editable = [
        "country",
        "active",
        "postage_price",
        "max_weight",
        "max_size",
        "placement_fee",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
        "expiry_date_required",
        "position",
    ]

    list_filter = ("active",)


@admin.register(models.FBAOrder)
class FBAOrderAdmin(admin.ModelAdmin):
    """Model admin for the FBAOrder models."""

    fields = [
        "region",
        "product",
        "product_weight",
        "product_hs_code",
        "product_asin",
        "product_purchase_price",
        "FBA_fee",
        "selling_price",
        "on_hold",
        "is_combinable",
        "aproximate_quantity",
        "quantity_sent",
        "box_weight",
        "closed_at",
        "fulfilled_by",
        "notes",
        "priority",
    ]

    list_display = [
        "__str__",
        "region",
        "created_at",
        "modified_at",
        "notes",
        "closed_at",
        "product",
        "product_weight",
        "product_hs_code",
        "product_asin",
        "product_purchase_price",
        "on_hold",
        "is_combinable",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "quantity_sent",
        "box_weight",
        "priority",
        "fulfilled_by",
    ]

    search_fields = [
        "product__sku",
        "product__product_range__name",
        "product_asin",
    ]

    date_hierarchy = "created_at"

    list_filter = ["region"]


@admin.register(models.FBAShipmentDestination)
class FBAShipmentDestinationAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentDestination model."""

    fields = (
        "name",
        "is_enabled",
        "recipient_name",
        "contact_telephone",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
        "country_iso",
        "postcode",
    )
    list_display = (
        "__str__",
        "name",
        "is_enabled",
        "recipient_name",
        "contact_telephone",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
        "country_iso",
        "postcode",
    )
    list_editable = (
        "name",
        "is_enabled",
        "recipient_name",
        "contact_telephone",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
        "country_iso",
        "postcode",
    )


@admin.register(models.FBAShipmentExport)
class FBAShipmentExportAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentExport model."""

    list_display = ("created_at",)


@admin.register(models.FBAShipmentMethod)
class FBAShipmentMethodAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentMethod model."""

    fields = ("name", "identifier", "priority", "is_enabled")
    list_display = ("__str__", "name", "identifier", "priority", "is_enabled")
    list_editable = ("name", "identifier", "priority", "is_enabled")


@admin.register(models.FBAShipmentOrder)
class FBAShipmentOrderAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentOrder model."""

    fields = (
        "export",
        "destination",
        "shipment_method",
        "is_on_hold",
    )
    list_display = (
        "__str__",
        "export",
        "destination",
        "shipment_method",
        "is_on_hold",
    )
    list_editable = (
        "destination",
        "shipment_method",
        "is_on_hold",
    )


@admin.register(models.FBAShipmentPackage)
class FBAShipmentPackageAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentPackage model."""

    fields = (
        "shipment_order",
        "length_cm",
        "width_cm",
        "height_cm",
    )
    list_display = (
        "__str__",
        "shipment_order",
        "length_cm",
        "width_cm",
        "height_cm",
    )
    list_editable = (
        "length_cm",
        "width_cm",
        "height_cm",
    )


@admin.register(models.FBAShipmentItem)
class FBAShipmentItemAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentItem model."""

    fields = (
        "package",
        "sku",
        "description",
        "quantity",
        "length_cm",
        "width_cm",
        "height_cm",
        "weight_kg",
        "value",
        "country_of_origin",
        "hr_code",
    )
    list_display = (
        "__str__",
        "package",
        "sku",
        "description",
        "quantity",
        "weight_kg",
        "value",
        "country_of_origin",
        "hr_code",
    )
    list_editable = (
        "sku",
        "description",
        "quantity",
        "weight_kg",
        "value",
        "country_of_origin",
        "hr_code",
    )


@admin.register(models.ShipmentConfig)
class ShipmentConfigAdmin(SingletonModelAdmin):
    """Model admin for the ShipmentConfig model."""

    exclude_fields = ()


@admin.register(models.FBAProfit)
class FBAProfitAdmin(admin.ModelAdmin):
    """Model admin for the FBAProfitAdmin model."""

    exclude_fields = ()


@admin.register(models.FBAProfitFile)
class FBAProfitFileAdmin(admin.ModelAdmin):
    """Model admin for the FBAProfitFile model."""

    exclude_fields = ()


@admin.register(models.ParcelhubAPIConfig)
class ParcelhubAPIConfigAdmin(SingletonModelAdmin):
    """Model admin for the ParcelhubAPIConfig model."""

    exclude_fields = ()
