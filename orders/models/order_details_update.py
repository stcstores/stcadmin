"""OrderDetailsUpdate stores records of order product details updates."""
import datetime

from django.db import models
from django.utils import timezone

from .product_sale import ProductSale


class OrderDetailsUpdateInProgressError(Exception):
    """Exception raised when attempting to start an update with one already in progress."""

    def __init__(self):
        """Raise Exception."""
        super().__init__(
            "Cannot start an Order Details Update as one is already in progress"
        )


class OrderDetailsUpdateManager(models.Manager):
    """Model manager for orders.OrderDetailsUpdate."""

    def start_update(self):
        """Update the ProductSale model."""
        if self.is_in_progress():
            raise OrderDetailsUpdateInProgressError()
        update = self.create()
        try:
            self._update_product_details(update)
        except Exception as e:
            update.mark_error()
            raise e
        else:
            update.mark_complete()
        return update

    def _update_product_details(self, update):
        for product_sale in ProductSale.objects.filter(details_success__isnull=True):
            try:
                product_sale.update_details()
            except Exception as e:
                OrderDetailsUpdateError.objects.create(
                    update=update, product_sale=product_sale, text=str(e)
                )

    def _timeout_update(self):
        """Set the status of updates older than TIMEOUT to ERROR."""
        self.filter(
            status=OrderDetailsUpdate.IN_PROGRESS,
            started_at__lte=timezone.now() - OrderDetailsUpdate.TIMEOUT,
        ).update(status=OrderDetailsUpdate.ERROR)

    def is_in_progress(self):
        """Return True if an update is in progress, else return False."""
        self._timeout_update()
        return self.filter(status=OrderDetailsUpdate.IN_PROGRESS).exists()


class OrderDetailsUpdate(models.Model):
    """Manages order product details updates from Cloud Commerce."""

    TIMEOUT = datetime.timedelta(hours=2)

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

    OrderDetailsUpdateInProgressError = OrderDetailsUpdateInProgressError

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=25, choices=STATUS_CHOICES, default=IN_PROGRESS
    )

    objects = OrderDetailsUpdateManager()

    class Meta:
        """Meta class for the OrderDetailsUpdate model."""

        verbose_name = "Order Details Update"
        verbose_name_plural = "Order Details Updates"

    def __str__(self):
        date = self.started_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"OrderDetailsUpdate {date} - {self.status}"

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


class OrderDetailsUpdateError(models.Model):
    """Record of errors retrieving product details for orders."""

    update = models.ForeignKey(OrderDetailsUpdate, on_delete=models.CASCADE)
    product_sale = models.ForeignKey(ProductSale, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        """Meta class for the OrderDetailsUpdateError model."""

        verbose_name = "Order Details Update Error"
        verbose_name_plural = "Order Details Update Errors"
