"""Model admin for the purchases app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from purchases import models


@admin.register(models.PurchaseSettings)
class PurchaseSettingsAdmin(SingletonModelAdmin):
    """Admin for the PurchaseSettings model."""

    exclude = ()


@admin.register(models.PurchaseExport)
class PurchaseExportAdmin(admin.ModelAdmin):
    """Admin for the PurchaseExport model."""

    exclude = ()


@admin.register(models.PurchasableShippingService)
class PurchasableShippingServiceAdmin(admin.ModelAdmin):
    """Admin for the PurchasableShippingService model."""

    exclude = ()
    list_display = ("shipping_service",)


@admin.register(models.ProductPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    """Admin for the ProductPurchase model."""

    exclude = ()
    raw_id_fields = ("product", "export")
    list_display = (
        "__str__",
        "purchased_by",
        "quantity",
        "export",
        "created_at",
        "to_pay",
        "product",
    )


@admin.register(models.ShippingPurchase)
class ShippingPurchaseAdmin(admin.ModelAdmin):
    """Admin for the ShippingPurchase model."""

    exclude = ()
    raw_id_fields = ("export",)
    list_display = (
        "__str__",
        "purchased_by",
        "quantity",
        "export",
        "created_at",
        "time_of_purchase_price",
        "shipping_service",
        "weight_grams",
        "to_pay",
    )


@admin.register(models.OtherPurchase)
class OtherPurchaseAdmin(admin.ModelAdmin):
    """Admin for the OtherPurchase model."""

    exclude = ()
    raw_id_fields = ("export",)
    list_display = (
        "__str__",
        "purchased_by",
        "quantity",
        "export",
        "created_at",
        "price",
        "description",
        "to_pay",
    )
