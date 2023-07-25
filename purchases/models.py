"""Models for the Purhcases app."""

from django.core.validators import MinValueValidator
from django.db import models, transaction
from solo.models import SingletonModel

from home.models import Staff
from inventory.models import BaseProduct


class PurchaseSettings(SingletonModel):
    """Model for storing settings for the purchases app."""

    purchase_charge = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    send_report_to = models.EmailField(null=True)

    class Meta:
        """Meta class for PurchaseSettings."""

        verbose_name = "Purchase Settings"


class PurchaseExportManager(models.Manager):
    """Manager for the PurchaseExport model."""

    @transaction.atomic
    def new_export(self):
        """Create a new purchase export."""
        purchases = Purchase.objects.filter(export__isnull=True)
        export = self.create()
        purchases.update(export=export)
        return export


class PurchaseExport(models.Model):
    """Model for purchase exports."""

    export_date = models.DateField(auto_now_add=True, unique=True)
    report_sent = models.BooleanField(default=False)

    objects = PurchaseExportManager()

    class Meta:
        """Meta class for PurchaseExport."""

        verbose_name = "Purchase Export"
        verbose_name_plural = "Purchase Exports"
        ordering = ("-export_date",)


class PurchaseManager(models.Manager):
    """Manager for the Purchase model."""

    def new_purchase(self, purchased_by, product, quantity):
        """Create a new purchase."""
        settings = PurchaseSettings.get_solo()
        purchase = self.create(
            purchased_by=purchased_by,
            product=product,
            quantity=quantity,
            time_of_purchase_item_price=product.purchase_price,
            time_of_purchase_charge=settings.purchase_charge,
        )
        purchase.full_clean()
        return purchase


class Purchase(models.Model):
    """Model for purchases."""

    purchased_by = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="purchases"
    )
    product = models.ForeignKey(
        BaseProduct, on_delete=models.PROTECT, related_name="staff_purchases"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    time_of_purchase_item_price = models.DecimalField(decimal_places=2, max_digits=8)
    time_of_purchase_charge = models.DecimalField(max_digits=4, decimal_places=2)
    export = models.ForeignKey(
        PurchaseExport,
        on_delete=models.PROTECT,
        related_name="purchases",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = PurchaseManager()

    class Meta:
        """Meta class for Purchase."""

        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.quantity} x {self.product.sku} for {self.purchased_by}"

    def to_pay(self):
        """Return the price to pay for this purchase."""
        return float(
            (self.time_of_purchase_item_price)
            * self.time_of_purchase_charge
            * self.quantity
        )
