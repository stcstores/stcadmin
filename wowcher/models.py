"""Models for the Wowcher app."""

from django.db import models
from django.utils import timezone


class ActiveDealManager(models.Manager):
    """Manager for currently active Wowcher deals."""

    def get_queryset(self):
        """Return a queryset of WowcherDeals that are currently active."""
        return super().get_queryset().filter(ended__isnull=True, inactive=False)


class WowcherDeal(models.Model):
    """Model for Wowcher deals."""

    deal_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    product_SKU = models.CharField(max_length=255)
    product_ID = models.CharField(max_length=255)
    item_net = models.DecimalField(max_digits=6, decimal_places=2)
    item_gross = models.DecimalField(max_digits=6, decimal_places=2)
    total_net = models.DecimalField(max_digits=6, decimal_places=2)
    total_gross = models.DecimalField(max_digits=6, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(blank=True, null=True, default=None)
    inactive = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveDealManager()

    class Meta:
        """Meta class for the WowcherDeal model."""

        verbose_name = "Wowcher Deal"
        verbose_name_plural = "Wowcher Deals"
        ordering = ("created",)

    def __str__(self):
        return f"Wowcher Deal {self.deal_id} - {self.name}"

    def end_deal(self):
        """Mark the Wowcher deal as ended."""
        self.ended = timezone.now()
        self.inactive = True
        self.save()


class OrderToDispatchManager(models.Manager):
    """ModelManager for Wowcher orders awaiting dispatch."""

    def get_queryset(self):
        """Return a queryset of WowcherOrders awaiting dispatch."""
        return (
            super()
            .get_queryset()
            .filter(
                canceled=False,
                status__in=[
                    WowcherOrder.STATUS_RECEIVED_BY_MERCHANT,
                    WowcherOrder.STATUS_READY_FOR_DESPATCH,
                ],
            )
        )


class WowcherOrder(models.Model):
    """Model for Wowcher orders."""

    STATUS_RECEIVED_BY_MERCHANT = "status_received_by_merchant"
    STATUS_READY_FOR_DESPATCH = "status_ready_for_despatch"
    STATUS_DESPATCHED = "status_despatched"
    STATUS_CHOICED = (
        (STATUS_RECEIVED_BY_MERCHANT, "Recieved by merchant"),
        (STATUS_READY_FOR_DESPATCH, "Ready for dispatch"),
        (STATUS_DESPATCHED, "Dispatched"),
    )

    deal = models.ForeignKey(WowcherDeal, on_delete=models.CASCADE)
    wowcher_code = models.CharField(max_length=255)
    cloud_commerce_order_ID = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICED)
    canceled = models.BooleanField(default=False)

    objects = models.Manager()
    to_dispatch = OrderToDispatchManager()

    class Meta:
        """Meta class for the WowcherOrder model."""

        verbose_name = "Wowcher Order"
        verbose_name_plural = "Wowcher Orders"

    def __str__(self):
        return f"Wowcher Order {self.wowcher_code}"
