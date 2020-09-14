"""Models for the FBA app."""

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse

from shipping.models import Country


class FBARegion(models.Model):
    """Model for regions in which FBA items are sold."""

    INCHES = "inches"
    CM = "cm"

    KG = "kg"
    LB = "lb"

    name = models.CharField(max_length=255)
    postage_price = models.PositiveIntegerField()
    max_weight = models.PositiveIntegerField(blank=True, null=True)
    max_size = models.FloatField(blank=True, null=True)
    dimension_unit = models.CharField(
        choices=((INCHES, "Inches"), (CM, "Centimeters")), max_length=10
    )
    weight_unit = models.CharField(
        choices=((LB, "Kilograms"), (KG, "Pounds")), max_length=2
    )

    class Meta:
        """Meta class for FBARegion."""

        verbose_name = "FBA Region"
        verbose_name_plural = "FBA Regions"

    def __str__(self):
        return self.name


class FBACountry(models.Model):
    """Model for countries in which FBA items are sold."""

    region = models.ForeignKey(
        FBARegion, on_delete=models.CASCADE, related_name="fba_regions"
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="fba_countries"
    )

    class Meta:
        """Meta class for FBACountry."""

        verbose_name = "FBA Country"
        verbose_name_plural = "FBA Countries"

    def __str__(self):
        return self.country.name


class FBAOrder(models.Model):
    """Model for FBA orders."""

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    fullfilled_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True
    )
    closed_at = models.DateTimeField(blank=True, null=True)
    region = models.ForeignKey(FBARegion, on_delete=models.CASCADE)
    product_SKU = models.CharField(max_length=20)
    product_ID = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    selling_price = models.PositiveIntegerField()
    FBA_fee = models.PositiveIntegerField()
    aproximate_quantity = models.PositiveIntegerField()
    quantity_sent = models.PositiveIntegerField(blank=True, null=True)
    box_width = models.PositiveIntegerField(blank=True, null=True)
    box_height = models.PositiveIntegerField(blank=True, null=True)
    box_depth = models.PositiveIntegerField(blank=True, null=True)
    box_weight = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    priority = models.PositiveIntegerField(default=999)

    class Meta:
        """Meta class for FBAOrder."""

        verbose_name = "FBA Order"
        verbose_name_plural = "FBA Orders"
        ordering = ["priority"]

    def is_closed(self):
        """Return True if the order is closed, otherwise False."""
        return self.closed_at is not None

    def get_absolute_url(self):
        """Return the URL of the update FBA order page."""
        return reverse("fba:update_fba_order", kwargs={"pk": self.pk})
