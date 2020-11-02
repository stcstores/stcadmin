"""Models for the FBA app."""

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from shipping.models import Country, Currency


class FBARegion(models.Model):
    """Model for regions in which FBA items are sold."""

    INCHES = "inches"
    CM = "cm"

    KG = "kg"
    LB = "lb"

    name = models.CharField(max_length=255)
    default_country = models.ForeignKey("FBACountry", on_delete=models.CASCADE)
    postage_price = models.PositiveIntegerField()
    max_weight = models.PositiveIntegerField(blank=True, null=True)
    max_size = models.FloatField(blank=True, null=True)
    dimension_unit = models.CharField(
        choices=((INCHES, "Inches"), (CM, "Centimeters")), max_length=10
    )
    weight_unit = models.CharField(
        choices=((LB, "Kilograms"), (KG, "Pounds")), max_length=2
    )
    auto_close = models.BooleanField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    flag = models.CharField(max_length=20, blank=True)

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


class AwaitingFulfillmentManager(models.Manager):
    """Model manager for FBA orders awaiting fulfillment."""

    def get_queryset(self):
        """Return a queryset of orders awaiting fulfillment."""
        return (
            super()
            .get_queryset()
            .exclude(status=FBAOrder.FULFILLED)
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


class FBAOrder(models.Model):
    """Model for FBA orders."""

    FULFILLED = "Fulfilled"
    AWAITING_BOOKING = "Awaiting Collection Booking"
    PRINTED = "Printed"
    NOT_PROCESSED = "Not Processed"

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    fulfilled_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True
    )
    closed_at = models.DateTimeField(blank=True, null=True)
    region = models.ForeignKey(FBARegion, on_delete=models.CASCADE)
    product_SKU = models.CharField(max_length=20)
    product_ID = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    product_weight = models.PositiveIntegerField()
    product_hs_code = models.CharField(max_length=255)
    selling_price = models.PositiveIntegerField()
    FBA_fee = models.PositiveIntegerField()
    aproximate_quantity = models.PositiveIntegerField()
    quantity_sent = models.PositiveIntegerField(blank=True, null=True)
    box_weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    notes = models.TextField(blank=True)
    priority = models.PositiveIntegerField(default=999)
    printed = models.BooleanField(default=False)
    small_and_light = models.BooleanField(default=False)
    status = models.CharField(
        choices=(
            (NOT_PROCESSED, NOT_PROCESSED),
            (AWAITING_BOOKING, AWAITING_BOOKING),
            (PRINTED, PRINTED),
            (FULFILLED, FULFILLED),
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

    def update_stock_level(self):
        """Update the product's stock level in Cloud Commerce."""
        print(f"Reduce stock level for {self.product_SKU} by {self.quantity_sent}")

    def get_status(self):
        """Return a string describing the status of the order."""
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
