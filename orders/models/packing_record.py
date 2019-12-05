"""The Packing Record model."""
from ccapi import CCAPI
from django.db import models

from print_audit.models import CloudCommerceUser

from .order import Order


class PackingRecord(models.Model):
    """Model for order packing."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    packed_by = models.ForeignKey(CloudCommerceUser, on_delete=models.PROTECT)

    class Meta:
        """Meta class for the Packing model."""

        verbose_name = "Packing Record"
        verbose_name_plural = "Packing Records"

    @classmethod
    def update(cls):
        """Update packing records from Cloud Commerce."""
        orders = cls._orders_to_update()
        for order in orders:
            cls._update_order(order)

    @classmethod
    def _orders_to_update(cls):
        missing_records = Order.dispatched.exclude(
            id__in=cls._default_manager.values_list("order", flat=True)
        )
        return missing_records.exclude(customer_ID__isnull=True)

    @classmethod
    def _update_order(cls, order):
        packer_ID = cls._get_packer_ID(order)
        if packer_ID is None:
            return
        try:
            packer = CloudCommerceUser.objects.get(user_id=packer_ID)
        except CloudCommerceUser.DoesNotExist:
            packer = CloudCommerceUser.objects.create(user_id=packer_ID)
        cls._default_manager.create(order=order, packed_by=packer)

    @classmethod
    def _get_packer_ID(cls, order):
        logs = CCAPI.customer_logs(order.customer_ID)
        for log in logs:
            if "Order Dispatched" in log.note and order.order_ID in log.note:
                return log.added_by_user_ID
