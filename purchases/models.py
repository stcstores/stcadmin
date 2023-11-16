"""Models for the Purhcases app."""

import csv
import datetime as dt
from io import StringIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
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
        purchases = BasePurchase.objects.filter(export__isnull=True)
        export = self.create(export_date=timezone.now() - dt.timedelta(days=1))
        purchases.update(export=export)
        return export


class PurchaseExport(models.Model):
    """Model for purchase exports."""

    export_date = models.DateField(default=timezone.now, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    report_sent = models.BooleanField(default=False)

    objects = PurchaseExportManager()

    class Meta:
        """Meta class for PurchaseExport."""

        verbose_name = "Purchase Export"
        verbose_name_plural = "Purchase Exports"
        ordering = ("-export_date",)

    def __str__(self):
        return f"Purchase Report {self.export_date}"

    def generate_report(self):
        """Return a .csv report as io.StringIO."""
        return PurchaseExportReport.generate_report_text(self)

    def get_report_filename(self):
        """Return a filename for .csv reports based on this expot."""
        return f"purchase_report_{self.export_date.strftime('%b_%Y')}.csv"

    def send_report_email(self):
        """Send montly staff purchase report email."""
        purchases_exist = self.purchases.count() > 0
        if purchases_exist:
            message_body = "Please find this months staff purchase report attached."
        else:
            message_body = "No staff purchases were made this month."
        message = EmailMessage(
            subject=f"Staff Purchases Report {self.export_date.strftime('%b %Y')}",
            body=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[PurchaseSettings.get_solo().send_report_to],
        )
        if purchases_exist:
            message.attach(
                self.get_report_filename(),
                self.generate_report().getvalue(),
                "text/csv",
            )
        message.send()


class BasePurchase(PolymorphicModel):
    """Base model for purchases."""

    purchased_by = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="purchases"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    export = models.ForeignKey(
        PurchaseExport,
        on_delete=models.PROTECT,
        related_name="purchases",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)


class ProductPurchaseManager(PolymorphicManager):
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


class ProductPurchase(BasePurchase):
    """Model for product purchases."""

    product = models.ForeignKey(
        BaseProduct, on_delete=models.PROTECT, related_name="staff_purchases"
    )

    time_of_purchase_item_price = models.DecimalField(decimal_places=2, max_digits=8)
    time_of_purchase_charge = models.DecimalField(max_digits=4, decimal_places=2)

    objects = ProductPurchaseManager()

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


class PurchaseExportReport:
    """Generate reports for purchase exports."""

    header = [
        "Purchased By",
        "SKU",
        "Product",
        "Quantity",
        "Date",
        "Item Price",
        "To Pay",
    ]

    @classmethod
    def generate_report_text(cls, export):
        """Return io.StringIO containing the report as a .csv."""
        rows = cls._get_report_data(cls._get_staff_purchases(export))
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output

    @staticmethod
    def _get_staff_purchases(export):
        staff_ids = export.purchases.values_list("purchased_by", flat=True)
        return {
            staff: export.purchases.filter(purchased_by=staff)
            for staff in Staff.objects.filter(id__in=staff_ids)
        }

    @staticmethod
    def _get_report_data(staff_purchases):
        rows = [PurchaseExportReport.header]
        for purchases in staff_purchases.values():
            for purchase in purchases:
                rows.append(PurchaseExportReport._get_purchase_row(purchase))
            rows.append(
                ["" for _ in range(6)] + [str(sum((_.to_pay() for _ in purchases)))]
            )
            rows.append([])
        return rows

    @staticmethod
    def _get_purchase_row(purchase):
        return [
            str(purchase.purchased_by),
            purchase.product.sku,
            purchase.product.full_name,
            purchase.quantity,
            str(purchase.created_at.date()),
            str(purchase.time_of_purchase_item_price),
            str(purchase.to_pay()),
        ]
