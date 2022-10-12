"""Models for managing FBA orders."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from inventory.models import BaseProduct
from linnworks.models import StockManager
from shipping.models import Country, Currency


class FBARegion(models.Model):
    """Model for regions in which FBA items are sold."""

    METRIC = "m"
    IMPERIAL = "i"

    unit_choices = ((METRIC, "Metric"), (IMPERIAL, "Imperial"))

    name = models.CharField(max_length=255)
    default_country = models.ForeignKey("FBACountry", on_delete=models.CASCADE)
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

    class Meta:
        """Meta class for FBARegion."""

        verbose_name = "FBA Region"
        verbose_name_plural = "FBA Regions"

    def __str__(self):
        return self.name

    def flag(self):
        """Return an image tag with the countries flag."""
        country = self.default_country.country
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


class AwaitingFulfillmentManager(models.Manager):
    """Model manager for FBA orders awaiting fulfillment."""

    def get_queryset(self):
        """Return a queryset of orders awaiting fulfillment."""
        return (
            super()
            .get_queryset()
            .exclude(status__in=(FBAOrder.FULFILLED, FBAOrder.ON_HOLD))
            .annotate(
                custom_order=models.Case(
                    models.When(status=FBAOrder.AWAITING_BOOKING, then=models.Value(0)),
                    models.When(status=FBAOrder.PRINTED, then=models.Value(1)),
                    models.When(status=FBAOrder.NOT_PROCESSED, then=models.Value(2)),
                    default=models.Value(3),
                    output_field=models.IntegerField(),
                )
            )
            .order_by("custom_order", "priority", "created_at")
        )


class ActiveFulfillmentCenter(models.Manager):
    """Manager for active fulfillment centers."""

    def get_queryset(self):
        """Return a queryset of active fulfillment centers."""
        return super().get_queryset().filter(inactive=False)


class FBAOrder(models.Model):
    """Model for FBA orders."""

    FULFILLED = "Fulfilled"
    AWAITING_BOOKING = "Awaiting Collection Booking"
    PRINTED = "Printed"
    NOT_PROCESSED = "Not Processed"
    ON_HOLD = "On Hold"
    MAX_PRIORITY = 999

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    fulfilled_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True
    )
    closed_at = models.DateTimeField(blank=True, null=True)
    region = models.ForeignKey(FBARegion, on_delete=models.CASCADE, blank=True)
    product_SKU = models.CharField(max_length=20)
    product_name = models.CharField(max_length=255)
    product_weight = models.PositiveIntegerField()
    product_hs_code = models.CharField(max_length=255)
    product_asin = models.CharField(max_length=24, blank=True)
    product_image_url = models.URLField(blank=True)
    product_supplier = models.CharField(max_length=255, blank=True)
    product_purchase_price = models.CharField(max_length=10)
    product_is_multipack = models.BooleanField(default=False)
    selling_price = models.PositiveIntegerField()
    FBA_fee = models.PositiveIntegerField()
    aproximate_quantity = models.PositiveIntegerField()
    quantity_sent = models.PositiveIntegerField(blank=True, null=True)
    box_weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    tracking_number = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    priority = models.PositiveIntegerField(default=MAX_PRIORITY)
    printed = models.BooleanField(default=False)
    small_and_light = models.BooleanField(default=False)
    on_hold = models.BooleanField(default=False)
    update_stock_level_when_complete = models.BooleanField(default=True)
    is_combinable = models.BooleanField(default=False)
    is_fragile = models.BooleanField(default=False)
    status = models.CharField(
        choices=(
            (NOT_PROCESSED, NOT_PROCESSED),
            (AWAITING_BOOKING, AWAITING_BOOKING),
            (PRINTED, PRINTED),
            (FULFILLED, FULFILLED),
            (ON_HOLD, ON_HOLD),
        ),
        max_length=255,
    )

    objects = models.Manager()
    awaiting_fulfillment = AwaitingFulfillmentManager()

    class Meta:
        """Meta class for FBAOrder."""

        verbose_name = "FBA Order"
        verbose_name_plural = "FBA Orders"
        ordering = ["priority"]

    def __str__(self):
        return f"{self.product_SKU} - {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        """Update the status field."""
        self.status = self.get_status()
        super().save(*args, **kwargs)

    def is_closed(self):
        """Return True if the order is closed, otherwise False."""
        return self.closed_at is not None

    def get_absolute_url(self):
        """Return the URL of the update FBA order page."""
        return reverse("fba:update_fba_order", kwargs={"pk": self.pk})

    def get_fulfillment_url(self):
        """Return the URL of the order's fulfillment page."""
        return reverse("fba:fulfill_fba_order", kwargs={"pk": self.pk})

    def details_complete(self):
        """Return True if all fields required to complete the order are filled."""
        return all(
            (
                self.box_weight is not None,
                self.quantity_sent is not None,
            )
        )

    def close(self):
        """Mark the order closed."""
        self.closed_at = timezone.now()
        self.save()

    def prioritise(self):
        """Mark the order as top priority."""
        FBAOrder.objects.filter(priority__lt=self.MAX_PRIORITY).update(
            priority=models.F("priority") + 1
        )
        self.priority = 1
        self.save()

    def update_stock_level(self, user):
        """Update the product's stock level in Cloud Commerce."""
        if settings.DEBUG is True:
            return messages.WARNING, "Stock update skipped: DEBUG mode"
        if self.update_stock_level_when_complete is False:
            return (
                messages.WARNING,
                (
                    f"Set to skip stock update, the stock level for {self.product_SKU}"
                    " is unchanged."
                ),
            )
        try:
            product = BaseProduct.objects.get(sku=self.product_SKU)
            stock_level = StockManager.get_stock_level(product)
            new_stock_level = stock_level - self.quantity_sent
            change_source = f"Updated by FBA order pk={self.pk}"
            StockManager.set_stock_level(
                product=product,
                user=user,
                new_stock_level=new_stock_level,
                change_source=change_source,
            )
            return messages.SUCCESS, (
                f"Changed stock level for {self.product_SKU} from {stock_level} "
                f"to {new_stock_level}"
            )
        except Exception:
            return (
                messages.ERROR,
                (
                    f"Stock Level failed to update for {self.product_SKU}, "
                    "please check stock level."
                ),
            )

    def set_tracking_number(self, tracking_number):
        """Set the order's tracking number."""
        self.tracking_number = tracking_number
        self.save()
        if self.status == self.AWAITING_BOOKING:
            self.close()

    def get_status(self):
        """Return a string describing the status of the order."""
        if self.on_hold:
            return self.ON_HOLD
        if self.closed_at is not None:
            return self.FULFILLED
        if self.details_complete() is True:
            return self.AWAITING_BOOKING
        if self.printed is True:
            return self.PRINTED
        return self.NOT_PROCESSED


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
