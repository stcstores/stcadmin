"""OrderUpdate stores records of order updates."""

import datetime

from django.db import models, transaction
from django.utils import timezone

from .order import Order
from .packing_record import PackingRecord


class OrderUpdateInProgressError(Exception):
    """Exception raised when attempting to start an update with one already in progress."""

    def __init__(self):
        """Raise Exception."""
        super().__init__("Cannot start an Order Update as one is already in progress")


class OrderUpdate(models.Model):
    """Manages order updates from Cloud Commerce."""

    TIMEOUT = datetime.timedelta(hours=1)

    COMPLETE = "Complete"
    IN_PROGRESS = "In Progress"
    ERROR = "Error"
    CANCELLED = "Cancelled"
    STATUS_CHOICES = (
        (COMPLETE, COMPLETE),
        (IN_PROGRESS, IN_PROGRESS),
        (ERROR, ERROR),
        (CANCELLED, CANCELLED),
    )

    OrderUpdateInProgressError = OrderUpdateInProgressError

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=25, choices=STATUS_CHOICES, default=IN_PROGRESS
    )

    class Meta:
        """Meta class for the OrderUpdate model."""

        verbose_name = "Order Update"
        verbose_name_plural = "Order Updates"

    def __str__(self):
        date = self.started_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"OrderUpdate {date} - {self.status}"

    @classmethod
    def update(cls):
        """Update the Order, PackingRecord and ProductSale models."""
        if cls.is_in_progress():
            raise OrderUpdateInProgressError()
        order_update = cls._default_manager.create()
        try:
            with transaction.atomic():
                Order.update()
                PackingRecord.update()
        except Exception as e:
            order_update.mark_error()
            raise e
        else:
            order_update.mark_complete()
        return order_update

    @classmethod
    def timeout_update(cls):
        """Set the status of updates older than TIMEOUT to ERROR."""
        cls.objects.filter(started_at__lte=timezone.now() - cls.TIMEOUT).update(
            status=cls.ERROR
        )

    @classmethod
    def is_in_progress(cls):
        """Return True if an update is in progress, else return False."""
        cls.timeout_update()
        return cls.objects.filter(status=cls.IN_PROGRESS).exists()

    @classmethod
    def latest(cls):
        """Return the latest update."""
        in_progress = cls._default_manager.filter(status=cls.IN_PROGRESS)
        if in_progress.exists():
            return in_progress.latest("started_at")
        else:
            return cls._default_manager.latest("completed_at")

    def mark_error(self):
        """Set error status."""
        self.completed_at = timezone.now()
        self.status = self.ERROR
        self.save()

    def mark_complete(self):
        """Set complete status."""
        self.completed_at = timezone.now()
        self.status = self.COMPLETE
        self.save()
