"""Models for managing FBA orders."""

from django.db import models
from django.utils.safestring import mark_safe

from shipping.models import Country, Currency


class FBARegion(models.Model):
    """Model for regions in which FBA items are sold."""

    METRIC = "m"
    IMPERIAL = "i"

    unit_choices = ((METRIC, "Metric"), (IMPERIAL, "Imperial"))

    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    postage_price = models.PositiveIntegerField(blank=True, null=True)
    postage_per_kg = models.PositiveIntegerField(default=0)
    postage_overhead_g = models.PositiveBigIntegerField(default=0)
    min_shipping_cost = models.PositiveBigIntegerField(blank=True, null=True)
    max_weight = models.PositiveIntegerField(blank=True, null=True)
    max_size = models.FloatField(blank=True, null=True)
    fulfillment_unit = models.CharField(choices=unit_choices, max_length=1)
    auto_close = models.BooleanField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    warehouse_required = models.BooleanField(default=False)
    expiry_date_required = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField(default=9999)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta class for FBARegion."""

        verbose_name = "FBA Region"
        verbose_name_plural = "FBA Regions"
        ordering = ("position",)

    def __str__(self):
        return self.name

    def flag(self):
        """Return an image tag with the countries flag."""
        return mark_safe(
            f'<img src="{self.country.flag.url}" height="20" '
            f'width="20" alt="{self.country.ISO_code}">'
        )

    def size_unit(self):
        """Return the size unit for the region."""
        if self.fulfillment_unit == self.METRIC:
            return "cm"
        else:
            return "inches"

    def weight_unit(self):
        """Return the weight unit for the region."""
        if self.fulfillment_unit == self.METRIC:
            return "kg"
        else:
            return "lb"

    def max_weight_local(self):
        """Return the maximum sendable weight in the fulfillment unit."""
        weight = self.max_weight
        if self.fulfillment_unit == self.IMPERIAL:
            weight *= 2.20462
        return f"{int(weight)} {self.weight_unit()}"

    def max_size_local(self):
        """Return the maximum sendable size in the fulfillment unit."""
        return f"{int(self.max_size)} {self.size_unit()}"

    def calculate_shipping(self, weight_grams):
        """Return the price for shipping a weight to this regsion.

        Args:
            weight_grams (int): The weight to be shipped in grams.

        Returns:
            int: The shipping cost in pence GBP.
        """
        if self.postage_price:
            return self.postage_price
        shipping_weight = weight_grams + self.postage_overhead_g
        calculated_postage_price = int(
            (float(shipping_weight) * self.postage_per_kg) / 1000
        )
        if calculated_postage_price < self.min_shipping_cost:
            return self.min_shipping_cost
        else:
            return calculated_postage_price


class FBATrackingNumberManager(models.Manager):
    """Manager for the FBATrackingNumber model."""

    def update_tracking_numbers(self, fba_order, *tracking_numbers):
        """
        Update the tracking numbers for an FBAOrder instance.

        Args:
            fba_order (fba.models.FBAOrder): The FBAOrder instance to update.
            *tracking_numbers (str): The updated list of tracking numbers.
        """
        self.filter(fba_order=fba_order).exclude(
            tracking_number__in=tracking_numbers
        ).delete()
        existing_tracking_numbers = set(
            self.filter(fba_order=fba_order).values_list("tracking_number", flat=True)
        )
        for tracking_number in set(tracking_numbers) - existing_tracking_numbers:
            self.create(fba_order=fba_order, tracking_number=tracking_number)


class FBATrackingNumber(models.Model):
    """Model for FBA tracking numbers."""

    fba_order = models.ForeignKey(
        "FBAOrder", on_delete=models.CASCADE, related_name="tracking_numbers"
    )
    tracking_number = models.CharField(max_length=255, blank=False)

    objects = FBATrackingNumberManager()

    class Meta:
        """Meta class for FBATrackingNumber."""

        verbose_name = "FBA Tracking Number"
        verbose_name_plural = "FBA Tracking Numbers"

    def __str__(self):
        return self.tracking_number
