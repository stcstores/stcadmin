"""Models for print_audit."""

import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from home.models import CloudCommerceUser


class CloudCommerceOrder(models.Model):
    """Model for Cloud Commerce Orders."""

    order_id = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    customer_id = models.CharField(max_length=10)
    trigger_id = models.CharField(max_length=10)
    date_completed = models.DateTimeField(blank=True, null=True)
    attempts = models.IntegerField()
    customer_order_dispatch_id = models.CharField(max_length=10)

    class Meta:
        """Meta class for CloudCommerceOrder."""

        verbose_name = "Cloud Commerce Order"
        verbose_name_plural = "Cloud Commerce Orders"

    @classmethod
    def create_from_print_queue(cls, print_log):
        """Create CloudCommerceOrder from an entry in the print queue."""
        try:
            user = CloudCommerceUser.objects.get(user_id=str(print_log.user_id))
        except ObjectDoesNotExist:
            return
        cls.objects.create(
            order_id=str(print_log.order_id),
            user=user,
            date_created=print_log.date_created,
            trigger_id=str(print_log.trigger_id),
            attempts=int(print_log.attempts),
            date_completed=(print_log.date_completed),
            customer_order_dispatch_id=str(print_log.customer_order_dispatch_id),
        )

    def save(self, *args, **kwargs):
        """Localise date created field."""
        self.date_created = self.localise_datetime(self.date_created)
        if self.date_completed:
            self.date_completed = self.localise_datetime(self.date_completed)
        super(CloudCommerceOrder, self).save(*args, **kwargs)

    def localise_datetime(self, date_input):
        """Return localised datetime.datetime object."""
        if date_input is not None and timezone.is_naive(date_input):
            tz = pytz.timezone("Europe/London")
            date_input = date_input.replace(tzinfo=tz)
        return date_input


class Breakage(models.Model):
    """Model for storing details of product breakages."""

    product_sku = models.CharField(max_length=20)
    order_id = models.CharField(max_length=10)
    note = models.TextField(blank=True, null=True)
    packer = models.ForeignKey(
        CloudCommerceUser, on_delete=models.CASCADE, related_name="old_breakage"
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta class for UserFeedback."""

        verbose_name = "Breakage"
        verbose_name_plural = "Breakages"
        ordering = ("timestamp",)

    def __str__(self):
        return "{} on order {}".format(self.product_sku, self.order_id)
