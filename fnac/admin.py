"""Model admin for the fnac app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from fnac import models

admin.site.register(models.FnacConfig, SingletonModelAdmin)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    """Model admin for fnac.Category."""

    fields = ("name", "english", "french")
    list_display = ("__str__", "name", "english", "french")
    list_editable = ("name",)


@admin.register(models.Size)
class SizeAdmin(admin.ModelAdmin):
    """Model admin for fnac.Size."""

    fields = ("name",)
    list_display = ("__str__", "name")
    list_editable = ("name",)


@admin.register(models.FnacRange)
class FnacRangeAdmin(admin.ModelAdmin):
    """Model admin for fnac.FnacRange."""

    fields = ("name", "sku", "category")
    list_display = ("__str__", "name", "sku", "category")
    list_editable = ("name", "sku", "category")


@admin.register(models.FnacProduct)
class FnacProductAdmin(admin.ModelAdmin):
    """Model admin for fnac.FnacProduct."""

    fields = (
        "name",
        "sku",
        "fnac_range",
        "barcode",
        "description",
        "price",
        "brand",
        "colour",
        "english_size",
        "french_size",
        "stock_level",
        "image_1",
        "image_2",
        "image_3",
        "image_4",
        "do_not_create",
        "created",
    )
    list_display = (
        "__str__",
        "name",
        "sku",
        "fnac_range",
        "barcode",
        "description",
        "price",
        "brand",
        "colour",
        "english_size",
        "french_size",
        "stock_level",
        "do_not_create",
        "created",
    )


@admin.register(models.Translation)
class TranslationAdmin(admin.ModelAdmin):
    """Model admin for fnac.Translation."""

    fields = ("product", "name", "description", "colour")
    list_display = ("product", "name", "description", "colour")
    list_editable = ("name", "description", "colour")


@admin.register(models.MissingInformationExport)
class MissingInformationExportAdmin(admin.ModelAdmin):
    """Model admin for fnac.MissingInformationExport."""

    fields = ("status", "export")
    list_display = ("timestamp", "status", "export")


@admin.register(models.InventoryImport)
class InventoryImportAdmin(admin.ModelAdmin):
    """Model admin for fnac.InventoryImport."""

    fields = ("status", "export")
    list_display = ("timestamp", "status", "export")


@admin.register(models.OfferUpdate)
class OfferUpdateAdmin(admin.ModelAdmin):
    """Model admin for fnac.OfferUpdate."""

    fields = ("status", "export")
    list_display = ("timestamp", "status", "export")


@admin.register(models.MissingInformationImport)
class MissingInformationImportAdmin(admin.ModelAdmin):
    """Model admin for fnac.MissingInformationImport."""

    fields = ("status", "import_file")
    list_display = ("timestamp", "status", "import_file")


@admin.register(models.MiraklProductImport)
class MiraklProductImportAdmin(admin.ModelAdmin):
    """Model admin for fnac.MiraklProductImport."""

    fields = ("status", "import_file")
    list_display = ("timestamp", "status", "import_file")


@admin.register(models.TranslationUpdate)
class TranslationUpdateAdmin(admin.ModelAdmin):
    """Model admin for fnac.TranslationUpdate."""

    fields = ("status", "errors")
    list_display = ("timestamp", "status", "errors")
