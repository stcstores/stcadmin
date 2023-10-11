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
        country = self.country
        return mark_safe(
            f'<img src="{country.flag.url}" height="20" '
            f'width="20" alt="{country.ISO_code}">'
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


class FBATrackingNumber(models.Model):
    """Model for FBA tracking numbers."""

    fba_order = models.ForeignKey(
        "FBAOrder", on_delete=models.CASCADE, related_name="tracking_numbers"
    )
    tracking_number = models.CharField(max_length=255, blank=False)

    class Meta:
        """Meta class for FBATrackingNumber."""

        verbose_name = "FBA Tracking Number"
        verbose_name_plural = "FBA Tracking Numbers"

    def __str__(self):
        return self.tracking_number


class FBAShippingPrice(models.Model):
    """Model for prices to send items to FBA."""

    added = models.DateTimeField(auto_now_add=True)
    product_SKU = models.CharField(max_length=20, unique=True)
    price_per_item = models.PositiveIntegerField()

    class Meta:
        """Meta class for FBAShippingPrice."""

        verbose_name = "FBA Shipping Price"
        verbose_name_plural = "FBA Shipping Prices"

    def __str__(self):
        return f"Shipping Price: {self.product_SKU}"
