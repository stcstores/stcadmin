"""Admin for the channels app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from channels import models


@admin.register(models.shopify_models.ShopifyConfig)
class ShopifyConfigAdmin(SingletonModelAdmin):
    """Model admin for the ShopifyConfig model."""

    exclude_fields = ()


@admin.register(models.shopify_models.ShopifyTag)
class ShopifyTagAdmin(admin.ModelAdmin):
    """Model admin for the ShopifyTag model."""

    exclude_fields = ()


@admin.register(models.shopify_models.ShopifyListing)
class ShopifyListingAdmin(admin.ModelAdmin):
    """Model admin for the ShopifyListing model."""

    exclude_fields = ()
    search_fields = ("product_range__name", "product_range__sku")
    autocomplete_fields = ("product_range",)
    list_select_related = ("product_range",)


@admin.register(models.shopify_models.ShopifyVariation)
class ShopifyVariationAdmin(admin.ModelAdmin):
    """Model admin for the ShopifyVariation model."""

    exclude_fields = ()
    list_display = ("__str__", "price")
    autocomplete_fields = ("listing", "product")
    list_select_related = ("listing", "product")


@admin.register(models.shopify_models.ShopifyUpdate)
class ShopifyUpdateManager(admin.ModelAdmin):
    """Model admin for the ShopifyUpdate model."""

    exclude_fields = ()
    list_display = ("listing", "operation_type", "created_at", "completed_at", "error")
