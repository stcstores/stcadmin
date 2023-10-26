"""FBAOrder model."""

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.db.models import Case, Value, When
from django.shortcuts import reverse
from django.utils import timezone

from home.models import Staff
from inventory.models import BaseProduct
from linnworks.models import StockManager

from .fba import FBATrackingNumber


class FBAOrderQueryset(models.QuerySet):
    """Custom queryset for FBAOrders."""

    def on_hold(self):
        """Return a queryset of on hold orders."""
        return self.filter(status=FBAOrder.ON_HOLD)

    def stopped(self):
        """Return a queryset of stopped orders."""
        return self.filter(status=FBAOrder.STOPPED)

    def fulfilled(self):
        """Return a queryset of fulfilled orders."""
        return self.filter(status=FBAOrder.FULFILLED)

    def awaiting_booking(self):
        """Return a queryset of orders awaiting booking."""
        return self.filter(status=FBAOrder.READY)

    def printed(self):
        """Return a queryset of printed orders."""
        return self.filter(status=FBAOrder.PRINTED)

    def not_processed(self):
        """Return a queryset of orders that are not processed."""
        return self.filter(status=FBAOrder.NOT_PROCESSED)

    def awaiting_fulfillment(self):
        """Return a queryset of orders that are waiting to be fulfilled."""
        return self.exclude(
            status__in=(FBAOrder.FULFILLED, FBAOrder.ON_HOLD, FBAOrder.STOPPED)
        )

    def unfulfilled(self):
        """Return a queryset of orders that are unfulfilled."""
        return self.exclude(status=FBAOrder.FULFILLED)

    def prioritised(self):
        """Return a queryset of orders that are prioritised."""
        return self.filter(priority__lt=FBAOrder.MAX_PRIORITY)

    def unprioritised(self):
        """Return a queryset of orders that are not prioritised."""
        return self.exclude(priority__lt=FBAOrder.MAX_PRIORITY)

    def order_by_priority(self):
        """Return a queryset of orders awaiting fulfullment ordered by status and priority."""
        return (
            self.awaiting_fulfillment()
            .annotate(
                custom_order=Case(
                    When(status=FBAOrder.READY, then=Value(0)),
                    When(status=FBAOrder.PRINTED, then=Value(1)),
                    When(status=FBAOrder.NOT_PROCESSED, then=Value(2)),
                    default=Value(3),
                    output_field=models.IntegerField(),
                )
            )
            .order_by("custom_order", "priority", "created_at")
        )


class FBAOrderManager(models.Manager):
    """Model manager for the FBAOrder model."""

    def get_queryset(self):
        """Return a queryset of FBAOrders annotated with status."""
        return FBAOrderQueryset(self.model, using=self._db).annotate(
            status=Case(
                When(closed_at__isnull=False, then=Value(FBAOrder.FULFILLED)),
                When(is_stopped=True, then=Value(FBAOrder.STOPPED)),
                When(on_hold=True, then=Value(FBAOrder.ON_HOLD)),
                When(
                    box_weight__isnull=False,
                    quantity_sent__isnull=False,
                    then=Value(FBAOrder.READY),
                ),
                When(printed=True, then=Value(FBAOrder.PRINTED)),
                default=Value(FBAOrder.NOT_PROCESSED),
                output_field=models.CharField(),
            )
        )

    def on_hold(self):
        """Return a queryset of on hold orders."""
        return self.get_queryset().on_hold()

    def stopped(self):
        """Return a queryset of stopped orders."""
        return self.get_queryset().stopped()

    def fulfilled(self):
        """Return a queryset of fulfilled orders."""
        return self.get_queryset().fulfilled()

    def awaiting_booking(self):
        """Return a queryset of orders awaiting booking."""
        return self.get_queryset().awaiting_booking()

    def printed(self):
        """Return a queryset of printed orders."""
        return self.get_queryset().printed()

    def not_processed(self):
        """Return a queryset of orders that are not processed."""
        return self.get_queryset().not_processed()

    def awaiting_fulfillment(self):
        """Return a queryset of orders that are waiting to be fulfilled."""
        return self.get_queryset().awaiting_fulfillment()

    def unfulfilled(self):
        """Return a queryset of orders that are unfulfilled."""
        return self.get_queryset().unfulfilled()

    def order_by_priority(self):
        """Return a queryset of orders awaiting fulfullment ordered by status and priority."""
        return self.get_queryset().order_by_priority()

    def prioritised(self):
        """Return a queryset of orders that are prioritised."""
        return self.get_queryset().prioritised()

    def unprioritised(self):
        """Return a queryset of orders that are not prioritised."""
        return self.get_queryset().unprioritised()


class FBAOrder(models.Model):
    """Model for FBA orders."""

    FULFILLED = "Fulfilled"
    READY = "Ready"
    PRINTED = "Printed"
    NOT_PROCESSED = "Not Processed"
    ON_HOLD = "On Hold"
    STOPPED = "Stopped"

    MAX_PRIORITY = 999

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    fulfilled_by = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="fulfilled_fba_orders",
    )
    closed_at = models.DateTimeField(blank=True, null=True)
    region = models.ForeignKey("FBARegion", on_delete=models.CASCADE, blank=True)
    product = models.ForeignKey(
        BaseProduct,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="fba_orders",
    )
    product_weight = models.PositiveIntegerField()
    product_hs_code = models.CharField(max_length=255)
    product_asin = models.CharField(max_length=24)
    product_purchase_price = models.CharField(max_length=10)
    product_is_multipack = models.BooleanField(default=False)
    selling_price = models.PositiveIntegerField()
    FBA_fee = models.PositiveIntegerField()
    aproximate_quantity = models.PositiveIntegerField()
    quantity_sent = models.PositiveIntegerField(blank=True, null=True)
    box_weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    notes = models.TextField(blank=True)
    priority = models.PositiveIntegerField(default=MAX_PRIORITY)
    printed = models.BooleanField(default=False)
    small_and_light = models.BooleanField(default=False)
    on_hold = models.BooleanField(default=False)
    update_stock_level_when_complete = models.BooleanField(default=True)
    is_combinable = models.BooleanField(default=False)
    is_fragile = models.BooleanField(default=False)
    is_stopped = models.BooleanField(default=False)
    stopped_reason = models.TextField(blank=True, null=True)
    stopped_at = models.DateField(blank=True, null=True)
    stopped_until = models.DateField(blank=True, null=True)

    objects = FBAOrderManager()

    class Meta:
        """Meta class for FBAOrder."""

        verbose_name = "FBA Order"
        verbose_name_plural = "FBA Orders"
        ordering = ["priority"]

    def __str__(self):
        return f"{self.product.sku} - {self.created_at.strftime('%Y-%m-%d')}"

    def is_prioritised(self):
        """Return True if the order has been prioritised, otherwise False."""
        return self.priority < self.MAX_PRIORITY

    def is_closed(self):
        """Return True if the order is closed, otherwise False."""
        return self.closed_at is not None

    def get_absolute_url(self):
        """Return the URL of the update FBA order page."""
        return reverse("fba:update_fba_order", kwargs={"pk": self.pk})

    def get_fulfillment_url(self):
        """Return the URL of the order's fulfillment page."""
        return reverse("fba:fulfill_fba_order", kwargs={"pk": self.pk})

    def close(self):
        """Mark the order closed."""
        self.closed_at = timezone.now()
        self.priority = self.MAX_PRIORITY
        self.on_hold = False
        self.stopped = False
        self.save()

    def details_complete(self):
        """Return True if all fields required to complete the order are filled."""
        return all(
            (
                self.box_weight is not None,
                self.quantity_sent is not None,
            )
        )

    def prioritise(self):
        """Mark the order as top priority."""
        FBAOrder.objects.filter(priority__lt=self.MAX_PRIORITY).exclude(
            status=self.FULFILLED
        ).update(priority=models.F("priority") + 1)
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
                    f"Set to skip stock update, the stock level for {self.product.sku}"
                    " is unchanged."
                ),
            )
        try:
            stock_level = StockManager.get_stock_level(self.product)
            new_stock_level = stock_level - self.quantity_sent
            change_source = f"Updated by FBA order pk={self.pk}"
            StockManager.set_stock_level(
                product=self.product,
                user=user,
                new_stock_level=new_stock_level,
                change_source=change_source,
            )
            return messages.SUCCESS, (
                f"Changed stock level for {self.product.sku} from {stock_level} "
                f"to {new_stock_level}"
            )
        except Exception:
            return (
                messages.ERROR,
                (
                    f"Stock Level failed to update for {self.product.sku}, "
                    "please check stock level."
                ),
            )

    def update_tracking_numbers(self, *tracking_numbers):
        """Update order tracking numbers."""
        for tracking_number in self.tracking_numbers.all():
            if tracking_number.tracking_number not in tracking_numbers:
                tracking_number.delete()
        for tracking_number in tracking_numbers:
            FBATrackingNumber.objects.get_or_create(
                fba_order=self, tracking_number=tracking_number
            )
        if len(tracking_numbers) > 0 and self.status == self.READY:
            self.close()
