"""Models for the Wowcher app."""

from django.db import models
from django.db.models import F
from django.utils import timezone


class ActiveDealManager(models.Manager):
    """Manager for currently active Wowcher deals."""

    def get_queryset(self):
        """Return a queryset of WowcherDeals that are currently active."""
        return super().get_queryset().filter(ended__isnull=True, inactive=False)


class WowcherDeal(models.Model):
    """Model for Wowcher deals."""

    deal_ID = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    shipping_price = models.DecimalField(max_digits=6, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    stock_alert_level = models.PositiveSmallIntegerField(default=3)
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
        return f"{self.deal_ID} - {self.name}"

    def end_deal(self):
        """Mark the Wowcher deal as ended."""
        self.ended = timezone.now()
        self.inactive = True
        WowcherStockLevelCheck.objects.filter(item__deal=self).delete()
        self.save()


class WowcherItem(models.Model):
    """Model for Wowcher products."""

    deal = models.ForeignKey(WowcherDeal, on_delete=models.CASCADE)
    wowcher_ID = models.CharField(max_length=20, unique=True, db_index=True)
    CC_SKU = models.CharField(max_length=12)
    CC_product_ID = models.CharField(max_length=20)
    hide_stock_alert = models.BooleanField(default=False)

    class Meta:
        """Meta class for the WowcherItem model."""

        verbose_name = "Wowcher Item"
        verbose_name_plural = "Wowcher Items"

    def wowcher_SKU(self):
        """Return the Wowcher SKU for the product."""
        return f"{self.deal.deal_ID}-{self.wowcher_ID}"

    def __str__(self):
        return self.wowcher_SKU()


class WowcherRedemptionFile(models.Model):
    """Model for Wowcher redemption files."""

    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class for the WowcherOrder model."""

        verbose_name = "Wowcher Redemption File"
        verbose_name_plural = "Wowcher Redemption Files"
        ordering = ("time_created",)

    def __str__(self):
        return f'Redemption File {self.time_created.strftime("%Y-%m-%d")}'


class WowcherProofOfDeliveryFile(models.Model):
    """Model for Wowcher redemption files."""

    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class for the WowcherOrder model."""

        verbose_name = "Wowcher Proof of Delivery File"
        verbose_name_plural = "Wowcher Proof of Delivery Files"
        ordering = ("time_created",)

    def __str__(self):
        return f'Proof of Delivery File {self.time_created.strftime("%Y-%m-%d")}'


class OrderToDispatchManager(models.Manager):
    """Manager for Wowcher orders awaiting dispatch."""

    def get_queryset(self):
        """Return a queryset of WowcherOrders awaiting dispatch."""
        return (
            super()
            .get_queryset()
            .filter(dispatched=False, canceled=False, CC_order_ID__isnull=False)
        )


class ForRedemptionFile(models.Manager):
    """Manager for WowcherOrder objects that should be added to a redemption file."""

    def get_queryset(self):
        """Return a queryset of WowcherOrders for a redemption file."""
        return (
            super()
            .get_queryset()
            .filter(dispatched=True, canceled=False, redemption_file=None)
        )


class ForProofOfDelivery(models.Manager):
    """Manager for WowcherOrder objects that should be added to a proof of delivery file."""

    def get_queryset(self):
        """Return a queryset of WowcherOrders for a proof of delivery file."""
        return (
            super()
            .get_queryset()
            .filter(dispatched=True, canceled=False, proof_of_delivery_file=None)
        )


class WowcherOrder(models.Model):
    """Model for Wowcher orders."""

    deal = models.ForeignKey(WowcherDeal, on_delete=models.CASCADE)
    wowcher_code = models.CharField(max_length=255, unique=True, db_index=True)
    customer_name = models.CharField(max_length=255)
    CC_order_ID = models.CharField(
        max_length=255, blank=True, null=True, default=None, unique=True
    )
    CC_customer_ID = models.CharField(
        max_length=255, blank=True, null=True, default=None, unique=True
    )
    tracking_code = models.CharField(max_length=255, unique=True, blank=True, null=True)
    item = models.ForeignKey(WowcherItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    dispatched = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    redemption_file = models.ForeignKey(
        WowcherRedemptionFile, on_delete=models.SET_NULL, null=True
    )
    proof_of_delivery_file = models.ForeignKey(
        WowcherProofOfDeliveryFile, on_delete=models.SET_NULL, null=True
    )
    time_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    to_dispatch = OrderToDispatchManager()
    for_redemption_file = ForRedemptionFile()
    for_proof_of_delivery_file = ForProofOfDelivery()

    class Meta:
        """Meta class for the WowcherOrder model."""

        verbose_name = "Wowcher Order"
        verbose_name_plural = "Wowcher Orders"
        ordering = ("time_created",)

    def __str__(self):
        return self.wowcher_code

    def on_redemption_file(self):
        """Return True if the order has a redemption file, otherwise return False."""
        return self.redemption_file is not None

    def on_proof_of_delivery_file(self):
        """Return True if the order has a proof of delivery file, otherwise return False."""
        return self.proof_of_delivery_file is not None


class StockAlerts(models.Manager):
    """Manager for WowcherOrder objects that should be added to a proof of delivery file."""

    def get_queryset(self):
        """Return a queryset of WowcherOrders for a proof of delivery file."""
        return (
            super()
            .get_queryset()
            .filter(
                stock_level__lte=F("item__deal__stock_alert_level"),
                item__deal__inactive=False,
                item__deal__ended__isnull=True,
                item__hide_stock_alert=False,
            )
        )


class WowcherStockLevelCheck(models.Model):
    """Model for stock level checks of Wowcher items."""

    item = models.OneToOneField(WowcherItem, on_delete=models.CASCADE)
    stock_level = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    stock_alerts = StockAlerts()

    class Meta:
        """Meta class for the WowcherStockLevelCheck model."""

        verbose_name = "Wowcher Stock Level"
        verbose_name_plural = "Wowcher Stock Levels"
        ordering = ("timestamp",)

    def get_deal(self):
        """Return the deal to which the item belongs."""
        return self.item.deal

    def get_SKU(self):
        """Return the item's SKU."""
        return self.item.CC_SKU
