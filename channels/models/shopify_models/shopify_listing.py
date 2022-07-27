"""Models for managing Shopify listings."""

from django.db import models

from inventory.models import BaseProduct, ProductRange


class ShopifyTag(models.Model):
    """Model for Shopify product tags."""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ShopifyListing(models.Model):
    """Model for Shopify product listings."""

    product_range = models.OneToOneField(
        ProductRange,
        on_delete=models.CASCADE,
        related_name="shopify_listing",
        primary_key=False,
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(ShopifyTag, blank=True)

    def __str__(self):
        return self.product_range.sku


class ShopifyVariation(models.Model):
    """Model for Shopify product variants."""

    listing = models.ForeignKey(
        ShopifyListing, on_delete=models.CASCADE, related_name="variations"
    )
    product = models.OneToOneField(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="shopify_variation",
        primary_key=False,
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.product.sku
