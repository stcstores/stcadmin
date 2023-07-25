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


@admin.register(models.Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin for the Purchase model."""

    exclude = ()
    raw_id_fields = ("product", "export")
    list_display = (
        "__str__",
        "purchased_by",
        "product",
        "quantity",
        "export",
        "created_at",
        "to_pay",
    )
