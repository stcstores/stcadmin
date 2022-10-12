"""Models for reorder reports."""

import datetime as dt

from django.db import models
from django.utils.timezone import make_aware

from fba.models import FBAOrder
from inventory.models import BaseProduct, Supplier
from linnworks.models import StockManager
from orders.models import ProductSale

from .base import BaseReportDownload, BaseReportGenerator


class ReorderReportDownload(BaseReportDownload):
    """Model for managing redorder reports."""

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="reorder_reports"
    )
    date_from = models.DateField()
    date_to = models.DateField()

    class Meta:
        """Meta class for OrderExportDownload."""

        verbose_name = "Reorder Report Download"
        verbose_name_plural = "Reorder Report Downlaods"
        ordering = ("-created_at",)
        get_latest_by = "created_at"

    def _get_filename(self):
        date_from = self.date_from.strftime("%Y-%m-%d")
        date_to = self.date_to.strftime("%Y-%m-%d")
        return f"Reorder Report for {self.supplier} {date_from} - {date_to}.csv"

    def _get_report_generator(self):
        return ReorderReportGenerator


class ReorderReportGenerator(BaseReportGenerator):
    """Class for generating stock reorder reports."""

    SKU = "SKU"
    NAME = "Name"
    SUPPLIER = "Supplier"
    SUPPLIER_SKU = "Supplier SKU"
    SOLD = "Sold"
    SENT_TO_FBA = "Sent to FBA"
    LAST_SENT_TO_FBA = "Date Last Sent to FBA"
    AVAILABLE = "Available"

    header = [
        SKU,
        NAME,
        SUPPLIER,
        SUPPLIER_SKU,
        SOLD,
        SENT_TO_FBA,
        LAST_SENT_TO_FBA,
        AVAILABLE,
    ]

    def __init__(self, *args, **kwargs):
        """Get product stock levels."""
        super().__init__(*args, **kwargs)
        self.products = self._get_products(self.download_object.supplier)
        self.stock_levels = self._get_stock_levels(self.products)

    def get_row_kwargs(self):
        """Yield kwargs to be passed to self.make_row for each row."""
        for product in self.products:
            yield {"product": product}

    def make_row(self, product):
        """Return a report row for each product."""
        date_from = self._convert_date(self.download_object.date_from)
        date_to = self._convert_date(self.download_object.date_to)
        return {
            self.SKU: product.sku,
            self.NAME: product.full_name,
            self.SUPPLIER: product.supplier.name,
            self.SUPPLIER_SKU: product.supplier_sku,
            self.SOLD: self._get_sold_count(product, date_from, date_to),
            self.SENT_TO_FBA: self._get_sent_to_fba(product, date_from, date_to),
            self.LAST_SENT_TO_FBA: self._get_last_sent_to_fba(product),
            self.AVAILABLE: self._get_available_stock(
                product=product, stock_levels=self.stock_levels
            ),
        }

    @staticmethod
    def _get_products(supplier):
        return BaseProduct.objects.filter(supplier=supplier).variations().active()

    @staticmethod
    def _get_stock_levels(products):
        return StockManager.recorded_stock_level(products.values_list("sku", flat=True))

    @staticmethod
    def _get_sold_count(product, date_from, date_to):
        sold_count = ProductSale.objects.filter(
            sku=product.sku,
            order__dispatched_at__gte=date_from,
            order__dispatched_at__lt=date_to,
        ).aggregate(models.Sum("quantity"))["quantity__sum"]
        return sold_count or 0

    @staticmethod
    def _get_available_stock(product, stock_levels):
        try:
            return stock_levels[product.sku]["available_stock_level"]
        except KeyError:
            return 0

    @staticmethod
    def _get_sent_to_fba(product, date_from, date_to):
        sent_count = FBAOrder.objects.filter(
            product_SKU=product.sku, closed_at__gte=date_from, closed_at__lt=date_to
        ).aggregate(models.Sum("quantity_sent"))["quantity_sent__sum"]
        return sent_count or 0

    @staticmethod
    def _get_last_sent_to_fba(product):
        try:
            record = FBAOrder.objects.filter(
                product_SKU=product.sku, closed_at__isnull=False
            ).latest("closed_at")
        except FBAOrder.DoesNotExist:
            return "Never Sent"
        else:
            return record.closed_at.strftime("%Y-%m-%d")

    def _convert_date(self, date):
        """Return a datetime.date as a timezone aware datetime.datetime."""
        return make_aware(dt.datetime.combine(date, dt.datetime.min.time()))
