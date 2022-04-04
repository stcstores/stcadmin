"""Models for product attributes."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class VariationOption(models.Model):
    """Model for variation options."""

    class Meta:
        """Meta class for VariationOption."""

        verbose_name = "Variation Option"
        verbose_name_plural = "Variation Options"
        ordering = ("ordering",)

    name = models.CharField(max_length=50, unique=True)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ListingAttribute(models.Model):
    """Model for listing attributes."""

    class Meta:
        """Meta class for ListingAttribute."""

        verbose_name = "Listing Attribute"
        verbose_name_plural = "Listing Attributes"
        ordering = ("ordering",)

    name = models.CharField(max_length=50, unique=True)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class VariationOptionValue(models.Model):
    """Model for product variation option values."""

    product = models.ForeignKey(
        "BaseProduct",
        on_delete=models.CASCADE,
        related_name="variation_option_values",
    )
    variation_option = models.ForeignKey(
        VariationOption,
        on_delete=models.PROTECT,
        related_name="variation_option_values",
    )
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for VariationOptionValue."""

        verbose_name = "Variation Option Value"
        verbose_name_plural = "Variation Option Values"
        ordering = ("variation_option", "value")
        unique_together = ("product", "variation_option")

    def __str__(self):
        return (
            f"VariationOptionValue: {self.product.sku} - "
            f"{self.variation_option.name}"
        )


class ListingAttributeValue(models.Model):
    """Model for product listing attribute values."""

    product = models.ForeignKey(
        "BaseProduct",
        on_delete=models.CASCADE,
        related_name="listing_attribute_values",
    )
    listing_attribute = models.ForeignKey(
        ListingAttribute,
        on_delete=models.PROTECT,
        related_name="listing_attribute_values",
    )
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for ListingAttributeValue."""

        verbose_name = "Listing Attribute Value"
        verbose_name_plural = "Listing Attribute Values"
        ordering = ("value",)
        unique_together = ("product", "listing_attribute")

    def __str__(self):
        return (
            f"ListingAttributeValue: {self.product.sku} - "
            f"{self.listing_attribute.name}"
        )


class PackageType(models.Model):
    """Model for package types."""

    name = models.CharField(max_length=50, unique=True)
    large_letter_compatible = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for PackageType."""

        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"
        ordering = ("ordering",)

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Model for Brands."""

    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Brand."""

        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Model for manufacturers."""

    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Manufacturer."""

        verbose_name = "Manufacturer"
        verbose_name_plural = "Manufacturers"
        ordering = ("name",)

    def __str__(self):
        return self.name


class VATRate(models.Model):
    """Model for VAT rates."""

    name = models.CharField(max_length=50, unique=True)
    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1)]
    )
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for VAT Rate."""

        verbose_name = "VAT Rate"
        verbose_name_plural = "VAT Rates"
        ordering = ["ordering"]

    def __str__(self):
        return self.name
