"""The Packing Record model."""
from ccapi import CCAPI
from django.db import models

from home.models import CloudCommerceUser

from .order import Order


class PackingRecordManager(models.Manager):
    """Model manager for the orders.PackingRecord model."""

    def update_packing_records(self):
        """Update packing records from Cloud Commerce."""
        orders = self._orders_to_update()
        for order in orders:
            self._update_order(order)

    def _orders_to_update(self):
        return Order.objects.dispatched().filter(
            packingrecord__isnull=True, customer_ID__isnull=False
        )

    def _update_order(self, order):
        packer_ID = self._get_packer_ID(order)
        if packer_ID is None:
            return
        try:
            packer = CloudCommerceUser.objects.get(user_id=packer_ID)
        except CloudCommerceUser.DoesNotExist:
            packer = CloudCommerceUser.objects.create(user_id=packer_ID)
        packing_record = PackingRecord(order=order, packed_by=packer)
        packing_record.save()

    def _get_packer_ID(self, order):
        logs = CCAPI.customer_logs(order.customer_ID)
        for log in logs:
            if "Order Dispatched" in log.note and order.order_ID in log.note:
                return log.added_by_user_ID


class PackingRecord(models.Model):
    """Model for order packing."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    packed_by = models.ForeignKey(CloudCommerceUser, on_delete=models.PROTECT)

    objects = PackingRecordManager()

    class Meta:
        """Meta class for the Packing model."""

        verbose_name = "Packing Record"
        verbose_name_plural = "Packing Records"
