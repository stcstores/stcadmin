"""Models for storing prouct bays."""


from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone

from .product import Product


class Bay(models.Model):
    """Model for Warehouse Bays."""

    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        """Meta class for Bay."""

        verbose_name = "Bay"
        verbose_name_plural = "Bays"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductBayLink(models.Model):
    """Model for product bay links."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_bay_links"
    )
    bay = models.ForeignKey(
        Bay, on_delete=models.CASCADE, related_name="product_bay_links"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for the ProductBayLink model."""

        verbose_name = "Product Bay Link"
        verbose_name_plural = "Product Bay Links"
        unique_together = ("product", "bay")

    def __str__(self):
        return f"Bay Link: {self.product} - {self.bay}"


class ProductBayHistoryManager(models.Manager):
    """Model Manager for the ProductBayHistory model."""

    def add_product_to_bay(self, user, product, bay):
        """Add a bay to a product."""
        self.model(user=user, product=product, bay=bay, change=self.model.ADDED).save()
        ProductBayLink(product=product, bay=bay).save()

    def remove_product_from_bay(self, user, product, bay):
        """Remove a bay from a product."""
        self.model(
            user=user, product=product, bay=bay, change=self.model.REMOVED
        ).save()
        ProductBayLink.objects.filter(product=product, bay=bay).delete()

    def set_product_bays(self, user, product, bays):
        """Set bays for a product."""
        existing_links = ProductBayLink.objects.filter(product=product)
        bays_to_remove = [link.bay for link in existing_links.exclude(bay__in=bays)]
        bays_to_add = [
            bay
            for bay in bays
            if not existing_links.filter(product=product, bay=bay).exists()
        ]
        with transaction.atomic():
            for bay in bays_to_remove:
                self.remove_product_from_bay(user=user, product=product, bay=bay)
            for bay in bays_to_add:
                self.add_product_to_bay(user=user, product=product, bay=bay)


class ProductBayHistory(models.Model):
    """Log changes to product bays."""

    REMOVED = "removed"
    ADDED = "added"

    user = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="product_bay_changes"
    )
    timestamp = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_bay_changes"
    )
    bay = models.ForeignKey(
        Bay, on_delete=models.PROTECT, related_name="product_bay_changes"
    )
    change = models.CharField(
        choices=((REMOVED, "Removed"), (ADDED, "Added")), max_length=255
    )

    objects = ProductBayHistoryManager()

    class Meta:
        """Meta class for ProductBayChange."""

        verbose_name = "Product Bay History"
        verbose_name_plural = "Product Bay History"

    def __str__(self):
        return f"{self.product} {self.change} {self.bay}"
