"""Product Range models."""

from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .product_attribute import (
    ListingAttribute,
    ListingAttributeValue,
    VariationOptionValue,
)


class ProductRangeManager(models.Manager):
    """Manager for complete products."""

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of complete products."""
        return super().get_queryset(*args, **kwargs).filter(status=self.model.COMPLETE)


class CreatingProductRangeManager(models.Manager):
    """Manager for incomplete products."""

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of incomplete products."""
        return super().get_queryset(*args, **kwargs).filter(status=self.model.CREATING)


class ProductRange(models.Model):
    """Model for Product Ranges."""

    COMPLETE = "complete"
    CREATING = "creating"
    ERROR = "error"

    STATUS_CHOICES = (
        (COMPLETE, "Complete"),
        (CREATING, "Creating"),
        (ERROR, "Error"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CREATING)

    sku = models.CharField(
        max_length=255, unique=True, db_index=True, blank=False, null=False
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    amazon_search_terms = models.TextField(blank=True, default="")
    amazon_bullet_points = models.TextField(blank=True, default="")
    is_end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    managed_by = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="product_ranges"
    )
    created_at = models.DateField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    ranges = ProductRangeManager()
    creating = CreatingProductRangeManager()

    class Meta:
        """Meta class for Product Ranges."""

        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

    def __str__(self):
        return f"{self.sku}: {self.name}"

    def get_absolute_url(self):
        """Return the absolute url for the product range."""
        return reverse("inventory:product_range", kwargs={"range_pk": self.pk})

    def complete_new_range(self):
        """Make product range complete and active."""
        self.status = self.COMPLETE
        self.save()

    def has_variations(self):
        """Return True if the product has multiple variations, otherwise return False."""
        return self.products.count() > 1

    def variation_options(self):
        """Return the Range's variable product options."""
        return (
            VariationOptionValue.objects.filter(product__product_range=self)
            .values_list("variation_option__name", flat=True)
            .distinct()
            .order_by()
        )

    def listing_attributes(self):
        """Return the Range's listing product options."""
        return (
            ListingAttributeValue.objects.filter(product__product_range=self)
            .values_list("listing_attribute__name", flat=True)
            .distinct()
            .order_by()
        )

    def variation_option_values(self):
        """Return a dict of varition keys and values."""
        variation_values = VariationOptionValue.objects.filter(
            product__product_range=self
        ).order_by("variation_option", "value")
        variation_options = defaultdict(list)
        for value in variation_values:
            if value.value not in variation_options[value.variation_option]:
                variation_options[value.variation_option].append(value.value)
        return dict(variation_options)

    def variation_values(self):
        """Return a list of the product range's variation option values."""
        return (
            VariationOptionValue.objects.filter(product__product_range=self)
            .distinct()
            .order_by()
            .values_list("value", flat=True)
        )

    def listing_attribute_values(self):
        """Return a list of the product range's listing attribute values."""
        return (
            ListingAttribute.objects.filter(product__product_range=self)
            .values_list("value", flat=True)
            .distinct()
            .order_by()
        )
