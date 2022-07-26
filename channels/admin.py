"""Admin for the channels app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from channels import models


@admin.register(models.shopify_models.ShopifyConfig)
class ShopifyConfigAdmin(SingletonModelAdmin):
    """Model admin for the ShopifyConfig model."""

    exclude_fields = ()
