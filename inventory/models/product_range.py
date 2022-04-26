"""Product Range models."""

from collections import defaultdict

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone

from .barcode import Barcode


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
    name = models.CharField(
        max_length=255, unique=True, db_index=True, blank=False, null=False
    )
    description = models.TextField(blank=True, default="")
    search_terms = ArrayField(
        models.CharField(max_length=255), blank=True, null=True, size=5
    )
    bullet_points = ArrayField(
        models.CharField(max_length=255), blank=True, null=True, size=5
    )

    is_end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    managed_by = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="product_ranges"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    ranges = ProductRangeManager()
    creating = CreatingProductRangeManager()

    class Meta:
        """Meta class for Product Ranges."""

        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

        constraints = [models.UniqueConstraint(Lower("name"), name="name_unique")]

    def __str__(self):
        return f"{self.sku}: {self.name}"

    def get_absolute_url(self):
        """Return the absolute url for the product range."""
        return reverse("inventory:product_range", kwargs={"range_pk": self.pk})

    def complete_new_range(self, user):
        """Make product range complete and active."""
        for product in self.products.all():
            if not product.barcode:
                product.barcode = Barcode.get_barcode(user=user, used_for=product.sku)
                product.save()
        self.status = self.COMPLETE
        self.save()

    def has_variations(self):
        """Return True if the product has multiple variations, otherwise return False."""
        return self.products.count() > 1

    def variation_options(self):
        """Return the Range's variable product options."""
        return (
            self.products.filter(
                variation_option_values__variation_option__name__isnull=False
            )
            .values_list("variation_option_values__variation_option__name", flat=True)
            .order_by()
            .distinct()
        )

    def listing_attributes(self):
        """Return the Range's listing product options."""
        return (
            self.products.filter(
                listing_attribute_values__listing_attribute__name__isnull=False
            )
            .values_list("listing_attribute_values__listing_attribute__name", flat=True)
            .order_by()
            .distinct()
        )

    def variation_option_values(self):
        """Return a dict of varition keys and values."""
        qs = (
            self.products.filter(
                variation_option_values__variation_option__name__isnull=False
            )
            .values_list(
                "variation_option_values__variation_option__name",
                "variation_option_values__value",
            )
            .order_by(
                "variation_option_values__variation_option",
                "variation_option_values__value",
            )
            .distinct()
        )
        variation_options = defaultdict(list)
        for key, value in qs:
            variation_options[key].append(value)
        return dict(variation_options)

    def variation_values(self):
        """Return a list of the product range's variation option values."""
        return (
            self.products.filter(variation_option_values__value__isnull=False)
            .values_list("variation_option_values__value", flat=True)
            .order_by()
            .distinct()
        )

    def listing_attribute_values(self):
        """Return a list of the product range's listing attribute values."""
        return (
            self.products.filter(listing_attribute_values__isnulll=False)
            .values_list("listing_attribute_values__value", flat=True)
            .order_by()
            .distinct()
        )
