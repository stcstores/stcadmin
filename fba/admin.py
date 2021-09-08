"""Model Admin for the FBA app."""

from django.contrib import admin

from fba import models


@admin.register(models.FBARegion)
class FBARegionAdmin(admin.ModelAdmin):
    """Model admin for the FBARegion model."""

    fields = [
        "name",
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
    ]
    list_display = [
        "name",
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
    ]
    list_editable = [
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
    ]


@admin.register(models.FBACountry)
class FBACountryAdmin(admin.ModelAdmin):
    """Model admin for the FBACountry model."""

    fields = ["region", "country"]
    list_display = ["__str__", "region", "country"]
    list_editable = ["region", "country"]


@admin.register(models.FBAOrder)
class FBAOrderAdmin(admin.ModelAdmin):
    """Model admin for the FBAOrder models."""

    fields = [
        "region",
        "product_SKU",
        "product_ID",
        "product_name",
        "product_weight",
        "product_hs_code",
        "product_asin",
        "product_image_url",
        "product_purchase_price",
        "FBA_fee",
        "selling_price",
        "small_and_light",
        "on_hold",
        "is_combinable",
        "aproximate_quantity",
        "quantity_sent",
        "box_weight",
        "tracking_number",
        "closed_at",
        "fulfilled_by",
        "notes",
        "priority",
    ]

    list_display = [
        "__str__",
        "status",
        "region",
        "created_at",
        "modified_at",
        "notes",
        "closed_at",
        "product_SKU",
        "product_ID",
        "product_name",
        "product_weight",
        "product_hs_code",
        "product_asin",
        "product_purchase_price",
        "small_and_light",
        "on_hold",
        "is_combinable",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "quantity_sent",
        "box_weight",
        "tracking_number",
        "priority",
        "fulfilled_by",
    ]

    search_fields = [
        "product_SKU",
        "product_ID",
        "product_name",
        "product_asin",
        "tracking_number",
    ]

    date_hierarchy = "created_at"

    list_filter = ["region", "status"]


@admin.register(models.FBAShippingPrice)
class FBAShippingPriceAdmin(admin.ModelAdmin):
    """Model admin for the FBAShippingPrice model."""

    fields = ["product_SKU", "price_per_item"]
    list_display = ["__str__", "product_SKU", "price_per_item", "added"]
    list_editable = ["product_SKU", "price_per_item"]


@admin.register(models.FulfillmentCenter)
class FulfillmentCenterAdmin(admin.ModelAdmin):
    """Model admin for the FulfilmentCenter model."""

    fields = ("name", "country", "address_1", "address_2", "address_3")


@admin.register(models.FBAShipmentDestination)
class FBAShipmentDestinationAdmin(admin.ModelAdmin):
    """Model admin for the FBAShipmentDestination model."""

    fields = (
        "name",
        "is_enabled",
        "recipient_last_name",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
        "postcode",
    )
    list_display = (
        "__str__",
        "name",
        "is_enabled",
        "recipient_last_name",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
        "postcode",
    )
    list_editable = (
        "name",
        "is_enabled",
        "recipient_last_name",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
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
        "order",
        "length_cm",
        "width_cm",
        "height_cm",
        "weight_kg",
    )
    list_display = (
        "__str__",
        "order",
        "length_cm",
        "width_cm",
        "height_cm",
        "weight_kg",
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
